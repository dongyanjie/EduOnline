# 使用PyMysql连接mysql数据库
import pymysql

pymysql.install_as_MySQLdb()

# 引用apps.py的配置
default_app_config = 'organization.apps.OrganizationConfig'