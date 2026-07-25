import os
import aiofiles
import logging 
from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, HTTPException, Request
from fastapi.responses import JSONResponse
from helper.config import Settings, get_settings
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
from .schemas.data import ProcessRequest
from models.db_schemes import DataChunk, Asset
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models import AssetTypeEnum
logger = logging.getLogger('uvicorn.error')
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]
)

@data_router.post("/upload/{project_id}")
async def upload_file(request: Request, project_id: str, file: UploadFile,
                       app_settings: Settings = Depends(get_settings)):
    """
    Request parameter is used to access the request object, which contains information about the incoming HTTP request.
    included the app in the main.py file, and the request is passed to the function as a parameter.
    """
    # Get or create the project from database using the ProjectModel
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)

    # Validate the uploaded file
    is_valid, result_signal = DataController().validate_uploaded_file(file)
    
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal}
        )
    
  
    project_dir_path = ProjectController().get_project_path(project_id=project_id)

    # Generate a unique file name and save the file
    unique_file_path , file_id = DataController().generate_unique_file_path(original_file_name=file.filename
                                                                  , project_id=project_id)
    
    try:
        async with aiofiles.open(unique_file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:
        logger.error(f"Error occurred while uploading file: {e}")   
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
                }
          )
    # Store the assets into the database
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    
    asset_resource = Asset(
    asset_project_id = project.id,
    asset_type=AssetTypeEnum.FILE.value,
    asset_name = file_id,
    asset_size = os.path.getsize(unique_file_path)
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)
    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(asset_record.id)
                }
            )

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, 
                           process_request: ProcessRequest):

    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    # Get or create the project from database using the ProjectModel
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )
    project = await project_model.get_project_or_create_one(project_id=project_id)

    process_controller = ProcessController(project_id=project_id)

    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)

    projects_files_ids = {}

    if process_request.file_id:
        record = await asset_model.get_asset_record(asset_project_id=project.id,
                                                    asset_name=process_request.file_id)
        if record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content ={
                "signal": ResponseSignal.FILE_ID_ERROR.value
                 }
            )
        projects_files_ids = {record.id:record.asset_name}



    else:

        project_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value)

        projects_files_ids={
            project_file.id:project_file.asset_name
            for project_file in project_files
        }

    if len(projects_files_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.NO_FILES_ERROR.value
            }
            )

    chunk_model = await ChunkModel.creare_instance(
            db_client=request.app.db_client
        )
        
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)


    no_records = 0
    no_files = 0

    for asset_id,file_id in projects_files_ids.items():

        file_content = process_controller.get_file_content(file_id=file_id)

        if file_content is None:
            logger.error(f"Error while processing file: {file_id}")
            continue

        file_chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )

        if file_chunks == None or len(file_chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseSignal.PROCESSING_FAILED.value
                    }
            )
        

        file_chunk_records=[
            DataChunk(
                chunk_text= chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order= idx + 1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            )
            for idx, chunk in enumerate(file_chunks)
        ]

    
        no_records += await chunk_model.insert_many_chunks(chunks=file_chunk_records)
        no_files += 1
    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "chunks_inserted": no_records,
            "processed_files": no_files

        }
    )
