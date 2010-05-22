To retrieve a file from a remote repo, in a temp dir

 git init
 git fetch-pack --no-progress --thin --all --depth=0 <URI of repo>
 git cat-file blob SHA1:<path-to-file>

