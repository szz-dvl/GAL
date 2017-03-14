import os

__all__ = []

for file in os.listdir("./plugins"):
    if file.endswith("py") and not "__" in file:        
        __all__.append(os.path.split(file)[1].split(".")[0])
        
