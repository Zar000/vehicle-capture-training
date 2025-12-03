from ultralytics import YOLO

def main():
    model = YOLO("C:/Users/zaro/Documents/_Dev/aws/school_proj/runs/detect/train9/weights/best.pt")

    val_results = model.val()
    print(val_results)

    predictions = model.predict(source="C:/Users/zaro/Documents/_Dev/aws/school_proj/testimages/snapshot.jpg")

    for result in predictions:
        result.show()
        result.save("C:/Users/zaro/Documents/_Dev/aws/school_proj/predictions")

if __name__ == "__main__":
    main()
