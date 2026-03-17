# Requirements
Install docker and docker compose

# Prepare the config.yaml 
create a file config.yaml for the user to connect in the app 
```yaml
cookie:
  expiry_days: 30
  key: # To be filled with any string
  name: # To be filled with any string
credentials:
  usernames:
    jsmith:
      first_name: John
      last_name: Smith
      password: abc # Will be hashed automatically
```

# Run with docker
to run it do: 
```bash
docker compose up -d
```