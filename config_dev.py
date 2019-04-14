# logging setup
log_path = None
logger_name = None

# smtp server
smtp_host = None
smtp_port = None

addr = None
pwd = None

# mail receivers !!list!!
mail_receiver = None
if mail_receiver is None:
    mail_receiver = [addr]

# targets
target_log_file = "/mnt/blockchain/debug.log"
target_dir = "/tmp/post-man-python"

# message details
subject = "bitcoind alert notification"
attached_target_name = "bitcoin_debug.log"
