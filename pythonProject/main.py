import requests

# Define the URL with the provided latitude and longitude
url = "https://soil.narc.gov.np/crop/api/bmp/cauliflower/"

# Define your bearer token

# Set up the request headers with the bearer token
headers = {
    "email": "agrajpaudel1@gmail.com",
    "password": "huskar.1",
"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxMzE2MTQ5NCwiaWF0IjoxNzEzMDc1MDk0LCJqdGkiOiI1NzYyYzA1ODdjNTA0MDNlODczNDFmZjAzZjhkYTRlNiIsInVzZXJfaWQiOjQ4fQ._e6hY6N3fAy4kS2MHZ4MjcmioIV5CBcb0TEuu6E5G9Y",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzEzMDc1Mzk0LCJpYXQiOjE3MTMwNzUwOTQsImp0aSI6IjIzMmU5MTQ4YTAyYzQ3MThhNzBjMTJiNDFhOWQ2MTEyIiwidXNlcl9pZCI6NDh9.4sUIT8D9mQ1NnJh8nR7sKcTwW1AogGZ--US5MYJx_pg",
}
# Send GET request with headers and store the response
response = requests.get(url,data=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Print the response content
    print(response.text)
else:
    print("Failed to retrieve data. Status code:", response.status_code)
    print(response.text)
