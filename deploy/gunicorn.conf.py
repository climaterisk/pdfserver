import multiprocessing
import os

bind = "0.0.0.0:8181"
workers = multiprocessing.cpu_count() * 2 + 1

log_dir = "/tmp"
accesslog = os.path.join(log_dir, 'access.pdfserver.log')
errorlog = os.path.join(log_dir, 'error.pdfserver.log')
