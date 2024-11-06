import logging
import os
import sys
import codecs

def setup_logger(name):
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    logger = logging.getLogger(name)
    
    # Usuń istniejące handlery
    if logger.handlers:
        logger.handlers.clear()
    
    logger.setLevel(logging.INFO)
    
    # Handler do pliku - używamy utf-8
    file_handler = logging.FileHandler(f'logs/{name}.log', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Handler do konsoli
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(name)s - %(levelname)s - %(message)s'
    ))
    
    # Ustawiamy kodowanie dla handlera konsoli
    if sys.platform == 'win32':
        console_handler.setStream(codecs.getwriter('utf-8')(sys.stdout.buffer))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
