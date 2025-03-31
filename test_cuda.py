import torch
has_cuda = torch.cuda.is_available()
print(f"Has CUDA: {has_cuda}")
if has_cuda:
    print(f"CUDA version: {torch.version.cuda}")
    print(f"CUDA device count: {torch.cuda.device_count()}")
    print("CUDA device names:")
    for i in range(torch.cuda.device_count()):
        device = torch.cuda.get_device_name(i)
        print(f"- {device}")