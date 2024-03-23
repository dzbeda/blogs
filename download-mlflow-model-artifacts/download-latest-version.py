# This Python will download the latest version of the Model user specific stage
# To run the script type "python3 download-latest-version.py --mlflow_url HTTP://MlFlow-ip-fqdn:MlFlowIP --model_name Test --required_model_state Staging
# Please note that if you didn't include the parameters, the default value will be used

import os
import mlflow
import requests
import logging
import argparse

version_file_name = "model-version.txt"
log_file = '/tmp/model-artifacts-download-log.txt'


# Create argparse parser
parser = argparse.ArgumentParser()
# Add an argument
parser.add_argument('--destination_dir', type=str, required=False, default='./llm-model', help='This defines the folder on which the model artifacts will be saved. Default is ./llm-model')
parser.add_argument('--mlflow_url', type=str, required=False, default='http://1.1.1.1:1234', help='This defines the mlflow url and port. Example: http://x.x.x.x:yyyy. Default is http://1.1.1.1:1234' )
parser.add_argument('--model_name', type=str, required=False, default='Test model', help='This defines the model name from which you wish to download the artifacts. Default is "Test model"')
parser.add_argument('--required_model_state', type=str, required=False, default='Production', help='This defines the model stage, can be None, Staging, Production, Archived. Dfault is Production')
args = parser.parse_args()

print(args)

# Create Loger
logger = logging.getLogger(__name__)
logging.basicConfig(filename=log_file ,level=logging.INFO, filemode='w', format='%(asctime)s : %(levelname)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def verify_connection_to_mlflow():
    try:
        requests.get(args.mlflow_url,timeout=30)
    except:
        print(f'please check you connection to mlflow server {args.mlflow_url}')
        logger.error(f'please check you connection to mlflow server {args.mlflow_url}')
        exit()
    # Set the MLflow tracking URI
    mlflow.set_tracking_uri(args.mlflow_url)
    # Get the client for managing registered models
    client = mlflow.tracking.MlflowClient()
    logger.info(f'connection to mlflow server was established')
    return client


def get_model_latest_version(mflow_client):
    try:
        latest_version_model = mflow_client.get_latest_versions(name=args.model_name, stages=[args.required_model_state])
    except:
        print(f'Invalid Model Version stage: {args.required_model_state}. Value must be one of None, Staging, Production, Archived.')
        logger.error(f'Invalid Model Version stage: {args.required_model_state}. Value must be one of None, Staging, Production, Archived.')
        exit()
    logger.info(f'Metadata was fetched successfully. Stage: {args.required_model_state}  , version: {latest_version_model[0].version} ')
    return latest_version_model[0].version


def download_model_artifacts(latest_version_model):
    # Open destination folder for files download
    if not os.path.exists(args.destination_dir):
        os.makedirs(args.destination_dir)
        print(f"Directory {args.destination_dir} created successfully.")
        logger.info(f'Create {args.destination_dir} folder for artifacts download')
    else:
        print(f"Directory {args.destination_dir} already exists.")
        logger.info(f'folder {args.destination_dir} already exists')
    
    print(f'starting to download the model artifacts from {args.required_model_state} state ,  version {latest_version_model}. This will take a while')
    # Create a file that includes the state and version to be downloaded
    f = open(f'{args.destination_dir}/{version_file_name}',"w+")
    f.write(f'Model stage is: {args.required_model_state}  \n Model version is: {latest_version_model}')
    f.close
    # Download artifacts
    model_uri = f"models:/{args.model_name}/{latest_version_model}"
    mlflow.artifacts.download_artifacts(artifact_uri=model_uri, dst_path=args.destination_dir)
    logger.info(f'Model metadata details can be found in {version_file_name} file under folder {args.destination_dir}')
    logger.info(f'Model artifact files can be found under folder {args.destination_dir}')


def main():
    print(f'Log file can be found in {log_file}')
    mlflow_client = verify_connection_to_mlflow()
    latest_version_model = get_model_latest_version(mlflow_client)
    download_model_artifacts(latest_version_model)


 

if __name__ == '__main__':
    main()
