# Submodule Utils

Base utils for components and mixins for runner classes.
### Syncing
You need to sync this repo with a public repo on github to make singularity images.
#### Steps
 ```shell script
#https://gist.github.com/sangeeths/9467061#file-github-to-bitbucket

#Go to Github and create a new repository (its better to have an empty repo)
git clone git@github.com:user_id/repo_name.git
cd repo_name

#Now add Bitbucket repo as a new remote in Github called "sync"
git remote add sync git@bitbucket.org:user_id/repo_name.git

#Verify what are the remotes currently being setup for "repo_name". This following command should show "fetch" and "push" for two remotes i.e. "origin" and "sync"
git remote -v

#Now do a pull from the "master" branch in the "sync" remote 
git pull sync master

#Setup a local branch called "bitbucket" track the "sync" remote's "master" branch
git branch --trach bitbucket sync/master

#Now push the local "master" branch to the "origin" remote in Github.
git push -u origin master
``` 
#### Syncing
 ```shell script
#To pull changes from the original :
git pull sync master
git push 
```