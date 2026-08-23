"""
╔═══════════════════════════════════════════════════════════╗
║  ssh_manager.py — Async SSH Operations (Paramiko)         ║
║  Servers add, verify, deploy userbot, kill, ping          ║
║  Database: SQLite (via database.py)                       ║
║  Optimized with safe timeouts & non-blocking execution    ║
╚═══════════════════════════════════════════════════════════╝
"""

import time
import asyncio
import logging
import paramiko
import database

logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BLOCKING SSH FUNCTIONS (Executed inside worker threads)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _sync_verify_ssh(host: str, username: str, password: str, port: int = 22):
    """SSH connection verify karta hai (Sync function)"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=username, password=password, port=port, timeout=12)
        client.close()
        return True, "Connection Successful"
    except paramiko.AuthenticationException:
        return False, "Authentication Failed (Invalid Username or Password)"
    except paramiko.SSHException as e:
        return False, f"SSH Protocol Error: {str(e)}"
    except Exception as e:
        return False, f"Connection Failed: {str(e)}"


def _sync_ping_ssh(host: str, username: str, password: str, port: int = 22):
    """Server online/offline check karta hai (Sync function)"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=username, password=password, port=port, timeout=8)
        stdin, stdout, stderr = client.exec_command("echo 'online'", timeout=5)
        output = stdout.read().decode().strip()
        client.close()
        return True if output == 'online' else False
    except Exception:
        return False


def _sync_deploy_userbot(host: str, username: str, password: str, port: int, 
                         session_string: str, phone_number: str, api_id: int, api_hash: str):
    """Worker bot ko SSH pe background me deploy karta hai (Sync function)"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=username, password=password, port=port, timeout=15)
        
        # Clean phone tag for logging
        safe_phone = "".join(c for c in phone_number if c.isdigit() or c == '+')
        log_file = f"bot_{safe_phone}.log"
        
        # Export env vars and run worker in detached background process
        command = (
            f"export API_ID='{api_id}' API_HASH='{api_hash}' SESSION_STRING='{session_string}' && "
            f"nohup python3 worker.py > '{log_file}' 2>&1 &"
        )
        
        client.exec_command(command)
        time.sleep(2)  # Give time for initial spawn
        client.close()
        return True, "Userbot Deployed Successfully"
    except Exception as e:
        logger.error(f"Deploy Error on {host}: {e}")
        return False, str(e)


def _sync_kill_userbot(host: str, username: str, password: str, port: int, phone_number: str):
    """SSH me pkill command chala kar userbot ko stop karta hai (Sync function)"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=username, password=password, port=port, timeout=12)
        safe_phone = "".join(c for c in phone_number if c.isdigit() or c == '+')
        command = f"pkill -f '{safe_phone}' || pkill -f 'worker.py'"
        client.exec_command(command)
        client.close()
        return True, "Userbot Terminated Successfully"
    except Exception as e:
        return False, str(e)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ASYNC WRAPPER FUNCTIONS (Non-blocking)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def verify_and_add_ssh(host: str, username: str, password: str, port: int, admin_id: int):
    """
    SSH verify karo aur database me save karo.
    """
    is_connected, message = await asyncio.to_thread(
        _sync_verify_ssh, host, username, password, port
    )
    
    if not is_connected:
        return False, message
    
    try:
        server_id = await database.add_ssh_server(
            host=host,
            username=username,
            password=password,
            port=port,
            added_by=admin_id
        )
        return True, f"✅ Server Successfully Added! (ID: {server_id})"
    except Exception as e:
        logger.error(f"DB Error saving SSH: {e}")
        return False, "Failed to save server in database."


async def get_all_ssh_servers():
    """Saare servers return karo (Dashboard ke liye)"""
    return await database.get_ssh_servers()


async def get_least_loaded_server():
    """Load balancing: Sabse kam userbot wala server return karo"""
    return await database.get_least_loaded_server()


async def ping_ssh_server(server_id: int):
    """Server ka status check karo aur DB update karo"""
    server = await database.get_ssh_server(server_id)
    if not server:
        return False
    
    is_online = await asyncio.to_thread(
        _sync_ping_ssh, 
        server['host'], 
        server['username'], 
        server['password'], 
        server['port']
    )
    
    await database.update_ssh_online_status(server_id, 1 if is_online else 0)
    return is_online


async def delete_ssh_server(server_id: int):
    """SSH server delete karo"""
    await database.delete_ssh_server(server_id)
    return True, "🗑️ Server Deleted Successfully!"


async def deploy_userbot(server_id: int, session_string: str, phone_number: str, api_id: int, api_hash: str):
    """
    Userbot ko SSH pe deploy karo.
    """
    server = await database.get_ssh_server(server_id)
    if not server:
        return False, "Server not found in database."
    
    success, message = await asyncio.to_thread(
        _sync_deploy_userbot,
        server['host'],
        server['username'],
        server['password'],
        server['port'],
        session_string,
        phone_number,
        api_id,
        api_hash
    )
    
    if success:
        await database.increment_ssh_userbots(server_id)
    
    return success, message


async def kill_userbot(server_id: int, phone_number: str, user_id: int = None):
    """
    Userbot ko kill karo SSH se.
    """
    server = await database.get_ssh_server(server_id)
    if not server:
        return False, "Server not found in database."
    
    success, message = await asyncio.to_thread(
        _sync_kill_userbot,
        server['host'],
        server['username'],
        server['password'],
        server['port'],
        phone_number
    )
    
    if success:
        await database.decrement_ssh_userbots(server_id)
        if user_id:
            await database.set_user_active(user_id, 0)
    
    return success, message


async def check_all_servers_status():
    """Dashboard refresh karne par saare servers ka status parallel check karo"""
    servers = await database.get_ssh_servers()
    if not servers:
        return True
    tasks = [ping_ssh_server(server['id']) for server in servers]
    await asyncio.gather(*tasks, return_exceptions=True)
    return True
