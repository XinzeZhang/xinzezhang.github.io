---

title:      Remove the committed files in the gitignore
tags:
    -git
---


```
# Remove everything from the git cache (the files will stay in the file system).
$ git rm -r --cached .

# Re-add everything (they'll be added in the current state, changes included)
$ git add .

# Commit
$ git commit -m 'Remove all files in the .gitignore'

# Update the remote
$ git push origin master
```