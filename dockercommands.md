### to stop running containers
```bash
sudo docker stop $(sudo docker ps -qa)
```
## To remove containers
```bash
sudo docker rm $(sudo docker ps -qa)
```
## To remove docker images 
```bash
sudo docker rmi $(sudo docker ps -qa)
```

### To remove mounted volumes
```bash
sudo docker volume rm $(sudo docker volume ls -q)
```
### To remove   - all stopped containers - all networks not used by at least one container
### all images without at least one container associated to them
### all build cache
``` bash
sudo docker system prune --all
```