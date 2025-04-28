import os
import oss2  # 安装依赖库：pip install oss2
from oss2.models import PutObjectResult
from config import ALIYUN_OSS

class OSSUploader:
    """
    阿里云对象存储
    
    使用Python SDK时，大部分操作都是通过oss2.Bucket类进行上传、下载、删除文件等操作。
    """
    
    # 允许的文件类型
    IMAGE_ACCEPT = ["image/jpeg", "image/png", "image/gif"]
    VIDEO_ACCEPT = ["video/mp4", "video/quicktime"]
    
    def __init__(self):
        """初始化OSS客户端"""
        auth = oss2.Auth(
            ALIYUN_OSS["accessKeyId"], 
            ALIYUN_OSS["accessKeySecret"]
        )
        self.bucket = oss2.Bucket(
            auth, 
            ALIYUN_OSS["endpoint"], 
            ALIYUN_OSS["bucket"]
        )
        self.base_url = ALIYUN_OSS["baseUrl"]

    def upload_file(self, file_path: str, object_name: str | None = None) -> str:
        """
        上传文件到OSS
        :param file_path: 本地文件路径
        :param object_name: OSS存储路径(不包含bucket)
        :return: 文件访问URL
        """
        if not object_name:
            object_name = os.path.basename(file_path)
            
        with open(file_path, 'rb') as f:
            file_data = f.read()
            
        result = self.bucket.put_object(object_name, file_data)
        
        if result.status != 200:
            raise Exception(f"文件上传失败，状态码：{result.status}")
            
        return f"{self.base_url}{object_name}"
        
    def upload_image(self, file_path: str, object_name: str | None = None, max_size: int = 10) -> str:

        """
        上传图片文件
        :param file_path: 本地文件路径
        :param object_name: OSS存储路径
        :param max_size: 最大文件大小(MB)
        :return: 文件访问URL
        """
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        if file_size > max_size:
            raise Exception(f"图片大小超过限制({max_size}MB)")
            
        return self.upload_file(file_path, object_name)
        
    def upload_video(self, file_path: str, object_name: str | None = None, max_size: int = 100) -> str:
        """
        上传视频文件
        :param file_path: 本地文件路径
        :param object_name: OSS存储路径
        :param max_size: 最大文件大小(MB)
        :return: 文件访问URL
        """
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        if file_size > max_size:
            raise Exception(f"视频大小超过限制({max_size}MB)")
            
        return  self.upload_file(file_path, object_name)