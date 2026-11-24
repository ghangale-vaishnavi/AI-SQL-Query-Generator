from dotenv import load_dotenv; 
import os
load_dotenv()
print('Host:',os.getenv('MYSQL_HOST'))
print('User:',os.getenv('MYSQL_USER'))
print('password loaded:',
bool(os.getenv('MYSQL_PASSWORD')))