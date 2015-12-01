
ZhihuX
======

ZhihuX是仿照知乎制作的问答网站

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
用户系统：<br>
>>用户角色<br>
>>用户资料<br>
>>用户登录<br>
>>管理员的和谐大法<br>
>>用户之间的相互关注<br>
>>查看用户所发表的评论和回答<br>
>>对于未登录的访问者，以上功能全部无法使用<br>
>>等等...<br>

问题系统：<br>
>>提问题<br>
>>回答问题<br>
>>评论回答<br>
>>给问题点赞<br>
>>查看给问题点赞的人<br>

首页我是这么设计的：<br>
>>如果用户的关注者在10个一下，那么就按照时间顺序显示所有的回答，\\<br>
>>如果关注者在10个或以上，那么就按时间顺序显示所有关注者的回答<br>
  
其实还有很多功能想添加，但是一个人的力量终究有限，就这么多吧<br>
  
