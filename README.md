# Machine-learning-with-pre-trained-models

## Docker notes

- If you see a build error like:

	```
	Error: EACCES: permission denied, unlink 'frontend/.next/server/app-paths-manifest.json'
	```

	It usually means build artifacts in `frontend/.next` are owned by `root` (often created by a container run). Fix it by removing the folder and restoring ownership:

	```bash
	sudo rm -rf frontend/.next
	sudo chown -R $(id -u):$(id -g) frontend
	```

	Alternatively, when using `docker compose` in development the `docker-compose.yml` is configured to run services as the host UID/GID to avoid creating root-owned files.

- Note: Upgrading `next` to a newer version is recommended when you have time (the project currently uses `next@14.2.0`).