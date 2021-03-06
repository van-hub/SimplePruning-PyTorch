""" 对模型进行预训练（pretrain），用于之后的剪枝（prune） """

# 外部库
from __future__ import print_function
import torch.optim as optim
import torch.optim.lr_scheduler as lr_scheduler

# 自定义
from utils import *
from tqdm import tqdm  # 用于显示进度条
import config


if __name__ == "__main__":
    model_name = 'resnet18'
    checkpoint = 'resnet18'  # 保存的checkpoint文件的名称
    epochs = 2
    lr = 0.1
    lr_decay_ratio = 0.2
    weight_decay = 0.0005
    momentum = 0.9

    model = config.models(model_name)
    device = config.DEVICE
    model.to(device)

    train_loader, test_loader = get_cifar_loaders(config.DATA)
    optimizer = optim.SGD(
        [w for name, w in model.named_parameters() if not 'mask' in name],
        lr=lr,
        momentum=momentum,
        weight_decay=weight_decay)
    scheduler = lr_scheduler.CosineAnnealingLR(optimizer, epochs, eta_min=1e-10)  # 使用 SGDR方法随 epoch调整 lr
    criterion = nn.CrossEntropyLoss()

    global error_history
    error_history = []
    for epoch in tqdm(range(epochs)):
        train(model, train_loader, criterion, optimizer)
        validate(model, epoch, test_loader, criterion, checkpoint=checkpoint if epoch != 2 else checkpoint + '_init')
        scheduler.step()
