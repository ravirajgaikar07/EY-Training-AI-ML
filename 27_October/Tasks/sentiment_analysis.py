import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
model = DistilBertForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")

def detect_sentiment(input_text):
  inputs=tokenizer(input_text,return_tensors="pt")
  with torch.no_grad():
    logits=model(**inputs).logits
  predicted_class_id = logits.argmax().item()
  return model.config.id2label[predicted_class_id]

input_text = input("Enter sentence to classify: ")
print(f"Detected sentiment : {detect_sentiment(input_text)}")