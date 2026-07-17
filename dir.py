import os

def cdir(folder_name):

    current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    output_folder = os.path.join(current_dir, folder_name)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    return output_folder

