deploy-staging:
	@echo "Deploying to staging..."
	gcloud app deploy app.yaml --version=staging --no-promote
	@echo "Deployed to staging"

deploy-prod-a:
	@echo "Deploying to prod-a..."
	gcloud app deploy app.yaml --version=production-a --no-promote
	@echo "Deployed to prod-a"

deploy-prod-b:
	@echo "Deploying to prod-b..."
	gcloud app deploy app.yaml --version=production-b --no-promote
	@echo "Deployed to prod-b"

logs:
	gcloud app logs tail -s default