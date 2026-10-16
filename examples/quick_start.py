"""Example: Track a simple training run"""
import sys
import time
import random
from pathlib import Path

# Add SDK to path (before pip install)
sys.path.insert(0, str(Path(__file__).parent.parent / "sdk"))

from openml_studio import Client

def train_model(epochs: int, learning_rate: float):
    """Simulate model training"""
    metrics = []
    for epoch in range(epochs):
        # Simulate decreasing loss with noise
        train_loss = 1.0 * (0.8 ** epoch) + random.uniform(0, 0.1)
        val_loss = 1.1 * (0.8 ** epoch) + random.uniform(0, 0.15)
        accuracy = min(0.99, 0.5 + epoch * 0.08 + random.uniform(-0.02, 0.02))
        
        metrics.append({
            "epoch": epoch,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "accuracy": accuracy
        })
        time.sleep(0.1)  # Simulate training time
    
    return metrics

def main():
    client = Client("http://localhost:8000")
    
    # Hyperparameters
    learning_rate = 0.001
    epochs = 10
    batch_size = 32
    
    with client.start_run(
        project="quick-start",
        experiment="baseline",
        name="example-run",
        params={
            "learning_rate": learning_rate,
            "epochs": epochs,
            "batch_size": batch_size,
            "model": "simple-cnn"
        },
        dataset_name="mnist",
        dataset_version="1.0"
    ) as run:
        print(f"Started run: {run.run_id}")
        
        # Training loop
        metrics = train_model(epochs, learning_rate)
        
        # Log metrics
        for m in metrics:
            run.log_metric("train_loss", m["train_loss"], step=m["epoch"])
            run.log_metric("val_loss", m["val_loss"], step=m["epoch"])
            run.log_metric("accuracy", m["accuracy"], step=m["epoch"])
            print(f"Epoch {m['epoch']}: loss={m['train_loss']:.4f}, acc={m['accuracy']:.4f}")
        
        # Log final metrics
        final_metrics = metrics[-1]
        run.log_metric("final_accuracy", final_metrics["accuracy"])
        run.log_metric("final_loss", final_metrics["train_loss"])
        
        # Save and log a dummy model file
        model_path = Path("model.txt")
        model_path.write_text(f"Model trained with lr={learning_rate}, epochs={epochs}")
        run.log_artifact(str(model_path))
        model_path.unlink()  # Clean up
        
        print(f"\n✓ Run completed: {run.run_id}")
        print(f"View at: http://localhost:3000/runs/{run.run_id}")

if __name__ == "__main__":
    main()
