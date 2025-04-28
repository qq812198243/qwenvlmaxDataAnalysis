import os
from pdf2image import convert_from_path
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.auth.credentials import StsTokenCredential
from aliyunsdkoss.request.v20150512 import PutObjectRequest

class PDFConverter:
    def __init__(self, access_key_id, access_key_secret, security_token, endpoint, bucket_name):
        """
        初始化阿里云OSS客户端
        :param access_key_id: 阿里云AccessKey ID
        :param access_key_secret: 阿里云AccessKey Secret
        :param security_token: 安全令牌(使用STS时需要)
        :param endpoint: OSS Endpoint
        :param bucket_name: OSS Bucket名称
        """
        credentials = StsTokenCredential(access_key_id, access_key_secret, security_token)
        self.client = AcsClient(region_id='cn-hangzhou', credential=credentials)
        self.endpoint = endpoint
        self.bucket_name = bucket_name
    
    def pdf_to_images(self, pdf_path, output_folder=None, dpi=300, fmt='jpeg'):
        """
        将PDF转换为图片
        :param pdf_path: PDF文件路径
        :param output_folder: 输出文件夹(默认为PDF所在目录)
        :param dpi: 图片DPI
        :param fmt: 图片格式(jpeg/png)
        :return: 生成的图片路径列表
        """
        if output_folder is None:
            output_folder = os.path.dirname(pdf_path)
        
        images = convert_from_path(pdf_path, dpi=dpi, fmt=fmt)
        image_paths = []
        
        for i, image in enumerate(images):
            image_path = os.path.join(output_folder, f"page_{i+1}.{fmt}")
            image.save(image_path, fmt.upper())
            image_paths.append(image_path)
        
        return image_paths
    
    def upload_to_oss(self, file_path, object_name=None):
        """
        上传文件到阿里云OSS
        :param file_path: 本地文件路径
        :param object_name: OSS对象名称(默认为文件名)
        :return: 文件URL
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
        
        request = PutObjectRequest()
        request.set_BucketName(self.bucket_name)
        request.set_Key(object_name)
        request.set_FilePath(file_path)
        
        response = self.client.do_action_with_exception(request)
        return f"https://{self.bucket_name}.{self.endpoint}/{object_name}"

if __name__ == "__main__":
    # 示例用法
    converter = PDFConverter(
        access_key_id='your-access-key-id',
        access_key_secret='your-access-key-secret',
        security_token='your-security-token',
        endpoint='oss-cn-hangzhou.aliyuncs.com',
        bucket_name='your-bucket-name'
    )
    
    # 转换PDF为图片
    images = converter.pdf_to_images("input.pdf")
    
    # 上传图片到OSS
    for img in images:
        url = converter.upload_to_oss(img)
        print(f"Uploaded: {url}")