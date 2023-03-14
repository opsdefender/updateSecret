import http.client
import urllib
import json
import requests
import configparser

# Load the parameters from the config file
config = configparser.ConfigParser()
config.read('config.param')

vault_url = config.get('KEYVAULT', 'vault_url')
tenant_id = config.get('KEYVAULT', 'tenant_id')
client_id = config.get('KEYVAULT', 'client_id')
client_secret = config.get('KEYVAULT', 'client_secret')
azure_secret_name = config.get('KEYVAULT', 'azure_secret_name')
delinea_site = config.get('KEYVAULT', 'delinea_site')


# Set up the request URL and data to get an access token
url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret,
    "resource": "https://vault.azure.net"
}

# Send the request to get an access token
response = requests.post(url, data=data)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Extract the access token from the response JSON
    access_token = response.json()["access_token"]
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")

# Set up the request headers with the access token
headers = {
    "Authorization": f"Bearer {access_token}"
}


# Use HTTPS for requests
azure_url = f'{vault_url}/secrets/{azure_secret_name}?api-version=7.3'
headers = {
    'Authorization': f'Bearer {access_token}',
}
azure_secret_response = requests.get(azure_url, headers=headers, verify=True)

# Check the response status code
if azure_secret_response.status_code == 200:
    # Successful request
    azure_secret_value = azure_secret_response.json().get("value")
else:
    # Error occurred
    print(f"Error: {azure_secret_response.status_code} - {azure_secret_response.text}")

print(azure_secret_value)

#------------------------------------------------------------ DELINEA PART

delinea_site = config.get('KEYVAULT', 'delinea_site')
token = config.get('KEYVAULT', 'token')
delinea_secret_ID_to_change = config.get('KEYVAULT', 'delinea_secret_ID_to_change')

delinea_site = '[Your Secret Server Site]' #ex: http://domain.com/SecretServer
authApi = '/oauth2/token'
api = delinea_site + '/api/v1'

def UpdateSecret(token, secret):        
    headers = {'Authorization':'Bearer ' + token, 'content-type':'application/json'}
    secretId = secret['id']
    resp = requests.put(api + '/secrets/' + str(secretId), json=secret, headers=headers)    
    
    if resp.status_code not in (200, 304):
        raise Exception("Error updating Secret. %s %s" % (resp.status_code, resp))    
    return resp.json()

#REST call to retrieve a secret by ID
def GetSecret(token, secretId):
    headers = {'Authorization':'Bearer ' + token, 'content-type':'application/json'}
    resp = requests.get(api + '/secrets/' + str(secretId), headers=headers)    
    
    if resp.status_code not in (200, 304):
        raise Exception("Error retrieving Secret. %s %s" % (resp.status_code, resp))    
    return resp.json()

#Get secret with ID = 1

secret = GetSecret(token, delinea_secret_ID_to_change)

#Change secret values
updateValues = {'name':f'{azure_secret_value}' }
secret.update(updateValues)
updatedSecret = UpdateSecret(token, secret)
print("Updated Secret Name: " + updatedSecret['name'])
