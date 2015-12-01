
### my-flask-application
#####使用方法
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

#####实现功能：
用户系统：
  用户角色
  用户资料
  用户登录
  管理员的和谐大法
  用户之间的相互关注
  查看用户所发表的评论和回答
  对于未登录的访问者，以上功能全部无法使用
  等等...
问题系统：
  提问题
  回答问题
  评论回答
  给问题点赞
  查看给问题点赞的人
  
  
  
