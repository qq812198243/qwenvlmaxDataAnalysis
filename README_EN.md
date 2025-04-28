# qwenvlmaxDataAnalysis Project

## Project Introduction

This project uses Alibaba's Qwen-VL-Max model for multimodal data analysis, capable of recognizing image content and extracting structured information. Main features include:

1. Image content recognition
2. Information extraction and standardization
3. Saving results in JSON format

## Installation Steps

1. Clone the repository
```bash
git clone <repository_url>
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set environment variables
```bash
export DASHSCOPE_API_KEY="your_API_KEY"
```

## Usage

1. Place images to analyze in the `dataset` folder
2. Run the main program
```bash
python main.py
```
3. The program will automatically process images and generate results
4. Results are saved in the `output` folder

## Example Code

```python
# Recognize image content from URL
result = recognize_image_from_url("https://example.com/image.png")

# Run complete processing pipeline
result = graph.invoke({"input": "https://example.com/image.png"})
```

## Notes

1. Ensure Alibaba Cloud OSS upload credentials are properly configured
2. Supported image formats include PNG/JPG and other common formats
3. Result JSON files will be saved in the `output` directory