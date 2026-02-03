from platform_ds_toolkit.credentials.key_manager import generate_key
from platform_ds_toolkit.credentials.vault import CredentialVault

def main():
  try: generate_key()
  except: pass
  v=CredentialVault(); v.save_credentials('example/db',{'user':'u','password':'p'})

if __name__=='__main__': main()
