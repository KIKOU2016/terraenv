import os.path
import os
from dotenv import load_dotenv
import sys
import platform
import requests
from zipfile import ZipFile
from config import DOWNLOAD_PATH, VERSION_FILE

""" Download Required Terraform / Terragrunt Versions """


def download_program(program, version):

    operating_sys = sys.platform

    # Upsert download path
    not os.path.exists(DOWNLOAD_PATH) and os.mkdir(DOWNLOAD_PATH)

    if program == "terraform":
        url = "https://releases.hashicorp.com" + "/terraform/" + version + \
            "/terraform_" + version + "_" + operating_sys + "_amd64.zip"
    
    elif program == "terragrunt":
        url = "https://github.com/gruntwork-io/terragrunt/releases/download/v" + \
            version + "/terragrunt_" + operating_sys + "_amd64"
    
    if not os.path.exists(DOWNLOAD_PATH + program + "_" + version):

        print("Downloading", program, version, "from", url)

        binary = requests.get(url)
        
        if binary.status_code == 404:
            raise Exception("Invalid version, got 404 error !")
    
        dest_path = DOWNLOAD_PATH + program + "_" + version

        open(dest_path, 'wb').write(binary.content)

        if program == "terraform":
            
            with ZipFile(dest_path, 'r') as zip:
                zip.extract('terraform', path=DOWNLOAD_PATH)

            if os.path.exists(DOWNLOAD_PATH + '/' + program) and os.path.exists(dest_path):
                os.remove(dest_path)
                os.rename(DOWNLOAD_PATH + '/' + program, dest_path)
            
            else:
                raise Exception("Issue extracting terraform !!")

        os.chmod(dest_path, 0o755)
    else:
        print (program, version, "already downloaded")

""" Installs Required Terraform / Terragrunt Versions """


def install(args):
    
    program = args.program
    version = args.version

    if not version and os.path.exists(VERSION_FILE):
        load_dotenv(dotenv_path=VERSION_FILE)
        version = (os.getenv(program.upper()))
    
    if not version:
        print ("Please define version or add that to .terraenv file")
        sys.exit(1)


    dest_path = DOWNLOAD_PATH + program + "_" + version
    
    if program == "terraform":
        download_program(program, version)
    
    elif program == "terragrunt":
        download_program(program, version)
    
    else:
        raise Exception(
            'Invalid Arguement !! It should be either terraform / terragrunt')
    
    try:
        os.remove("/usr/local/bin/" + program )
    
    except FileNotFoundError:
        pass
    
    os.symlink(dest_path, "/usr/local/bin/" + program )