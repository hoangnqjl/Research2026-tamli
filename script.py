import torch
from torchvision import models, transforms
from PIL import Image

assert torch.cuda.is_available(), "PyTorch chưa hỗ trợ CUDA"
device = torch.device("cuda:0")
print("Đang chạy trên:", torch.cuda.get_device_name(0))

# Load AlexNet pretrained
weights = models.AlexNet_Weights.IMAGENET1K_V1
model = models.alexnet(weights=weights).to(device)
model.eval()

# Preprocess
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    ),
])

def predict_with_analysis_8layers(image_path):
    img = Image.open(image_path).convert("RGB")
    x = preprocess(img).unsqueeze(0).to(device)
    print("\nInput:", x.shape)

    with torch.no_grad():
        # 🔹 5 lớp convolutional (features)
        # AlexNet features: 0-12
        # Layer 1: Conv1 + ReLU + MaxPool (0-2)
        x = model.features[0](x)
        x = model.features[1](x)
        x = model.features[2](x)
        print("🔹 Conv Layer 1:", x.shape)

        # Layer 2: Conv2 + ReLU + MaxPool (3-5)
        x = model.features[3](x)
        x = model.features[4](x)
        x = model.features[5](x)
        print("🔹 Conv Layer 2:", x.shape)

        # Layer 3: Conv3 + ReLU (6-7)
        x = model.features[6](x)
        x = model.features[7](x)
        print("🔹 Conv Layer 3:", x.shape)

        # Layer 4: Conv4 + ReLU (8-9)
        x = model.features[8](x)
        x = model.features[9](x)
        print("🔹 Conv Layer 4:", x.shape)

        # Layer 5: Conv5 + ReLU + MaxPool (10-12)
        x = model.features[10](x)
        x = model.features[11](x)
        x = model.features[12](x)
        print("🔹 Conv Layer 5:", x.shape)

        # Flatten
        x = torch.flatten(x, 1)
        print("🔸 Flatten:", x.shape)

        # 🔸 3 lớp fully connected (classifier)
        for i, layer in enumerate(model.classifier):
            x = layer(x)
            if isinstance(layer, torch.nn.Linear):
                print(f"🔸 FC Layer {i} ({layer.__class__.__name__}): {x.shape}")

        # Dự đoán
        probs = torch.softmax(x[0], dim=0)
        prob, class_id = torch.max(probs, 0)
        label = weights.meta["categories"][class_id.item()]

    print(f"\n🎯 Dự đoán: {label}")
    print(f"📊 Độ tin cậy: {prob.item()*100:.2f}%")

if __name__ == "__main__":
    path = input("Nhập đường dẫn đến file ảnh: ").strip().replace('"', '').replace("'", "")
    predict_with_analysis_8layers(path)
