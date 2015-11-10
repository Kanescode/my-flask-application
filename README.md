
### my-flask-application
用命令python manage.py shell 进入shell模式 <br>
输入一下命令： <br>
from app import db <br>
db.create_all() <br>
Role.insert_roles() <br>
Ctrl + c 退出shell模式 <br>
输入python manage.py runserver 运行吧 <br>
在浏览器中输入地址localhost:5000进入网站 <br>

对了，在运行前要还要做两件事: <br>
修改config.py里的邮箱账号变为你自己的邮箱，这样你可以用自己的邮箱账号注册管理员账号 <br>
用set MAIL_USERNAME 和 set MAIL_PASSWORD 设置环境变量，值是你自己邮箱的账号和密码 <br>
