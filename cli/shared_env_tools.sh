# in rc
# [ -f "$HOME/.shared_env_tools.sh" ] && source "$HOME/.shared_env_tools.sh"

# Path to shared environment file
SHARED_ENV_FILE="$HOME/.shared_env"

# Load shared environment variables
load() {
  if [ -f "$SHARED_ENV_FILE" ]; then
    source "$SHARED_ENV_FILE"
    echo "[+] Loaded shared environment from $SHARED_ENV_FILE"
  else
    echo "[!] No shared environment file found at $SHARED_ENV_FILE"
  fi
}

# Store a variable: store name=value
store() {
  if [[ "$1" != *=* ]]; then
    echo "Usage: store name=value"
    return 1
  fi

  local pair="$1"
  local name="${pair%%=*}"
  local value="${pair#*=}"

  # Remove existing entry
  sed -i "/^export $name=/d" "$SHARED_ENV_FILE" 2>/dev/null

  # Append new entry
  echo "export $name=\"$value\"" >> "$SHARED_ENV_FILE"

  # Export it in the current shell
  export "$name=$value"

  echo "[+] Stored and exported: $name=$value"
}

# Remove a variable: remove name
remove() {
  if [ -z "$1" ]; then
    echo "Usage: remove name"
    return 1
  fi

  local name="$1"

  # Remove from the env file
  sed -i "/^export $name=/d" "$SHARED_ENV_FILE" 2>/dev/null

  # Unset from current session
  unset "$name"

  echo "[-] Removed variable: $name"
}

list() {
  if [ ! -f "$SHARED_ENV_FILE" ]; then
    echo "[!] No shared environment file found at $SHARED_ENV_FILE"
    return 1
  fi

  echo "[*] Stored environment variables:"
  grep '^export ' "$SHARED_ENV_FILE" | while read -r line; do
    var_name=$(echo "$line" | cut -d'=' -f1 | cut -d' ' -f2)
    var_value=$(eval echo "\$$var_name")
    echo "$var_name=\"$var_value\""
  done
}
