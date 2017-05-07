# encoding=utf-8
# Created by xupingmao on 2016/12

from handlers.base import *
import xauth
import xutils
import config

import web.db as db
from . import dao

def date2str(d):
    ct = time.gmtime(d / 1000)
    return time.strftime('%Y-%m-%d %H:%M:%S', ct)


def try_decode(bytes):
    try:
        return bytes.decode("utf-8")
    except:
        return bytes.decode("gbk")

class handler(BaseHandler):

    @xauth.login_required()
    def execute(self):
        id = self.get_argument("id", "")
        name = self.get_argument("name", "")
        if id == "" and name == "":
            raise HTTPError(504)
        if id != "":
            id = int(id)
            dao.visit_by_id(id)
            file = dao.get_by_id(id)
        elif name is not None:
            file = dao.get_by_name(name)
        if file is None:
            raise web.notfound()
        download_csv = file.related != None and "CODE-CSV" in file.related
        self.render(file=file, 
            content = file.get_content(), 
            date2str=date2str,
            download_csv = download_csv, 
            children = dao.get_children_by_id(file.id))

    def download_request(self):
        id = self.get_argument("id")
        file = dao.get_by_id(id)
        content = file.get_content()
        if content.startswith("```CSV"):
            content = content[7:-3] # remove \n
        web.ctx.headers.append(("Content-Type", 'application/octet-stream'))
        web.ctx.headers.append(("Content-Disposition", "attachment; filename=%s.csv" % quote(file.name)))
        return content

class MarkdownEdit(BaseHandler):

    @xauth.login_required()
    def default_request(self):
        id = self.get_argument("id", "")
        name = self.get_argument("name", "")
        if id == "" and name == "":
            raise HTTPError(504)
        if id != "":
            id = int(id)
            dao.visit_by_id(id)
            file = dao.get_by_id(id)
        elif name is not None:
            file = dao.get_by_name(name)
        if file is None:
            raise web.notfound()
        download_csv = file.related != None and "CODE-CSV" in file.related
        self.render("file/markdown_edit.html", file=file, 
            content = file.get_content(), 
            date2str=date2str,
            download_csv = download_csv, 
            children = dao.get_children_by_id(file.id))

def sqlite_escape(text):
    if text is None:
        return "NULL"
    if not (isinstance(text, str)):
        return repr(text)
    # text = text.replace('\\', '\\')
    text = text.replace("'", "''")
    return "'" + text + "'"

def result(success = True, msg=None):
    return {"success": success, "result": None, "msg": msg}

class UpdateHandler(BaseHandler):

    def default_request(self):
        is_public = self.get_argument("public", "")
        id = self.get_argument("id", type=int)

        content = self.get_argument("content")
        version = self.get_argument("version", type=int)

        file = dao.get_by_id(id)
        assert file is not None

        # 理论上一个人是不能改另一个用户的存档，但是可以拷贝成自己的
        # 所以权限只能是创建者而不是修改者
        groups = file.creator
        if is_public == "on":
            groups = "*"
        
        rowcount = dao.update(where = dict(id=id, version=version), 
            content=content, type="md", size=len(content), groups = groups)
        if rowcount > 0:
            raise web.seeother("/file/edit?id=" + str(id))
        else:
            # 传递旧的content
            cur_version = file.version
            file.content = content
            file.version = version
            return self.render("file/markdown_edit.html", file=file, 
            content = content, 
            date2str=date2str,
            children = dao.get_children_by_id(file.id),
            error = "更新失败, version冲突,当前version={},最新version={}".format(version, cur_version))

    def rename_request(self):
        fileId = self.get_argument("fileId")
        newName = self.get_argument("newName")
        record = dao.get_by_name(newName)

        fileId = int(fileId)
        old_record = dao.get_by_id(fileId)

        if old_record is None:
            return result(False, "file with ID %s do not exists" % fileId)
        elif record is not None:
            return result(False, "file %s already exists!" % repr(newName))
        else:
            # 修改名称不用乐观锁
            rowcount = dao.update(where= dict(id = fileId), name = newName)
            return result(rowcount > 0)

    def del_request(self):
        id = int(self.get_argument("id"))
        dao.update(where=dict(id=id), is_deleted=1)
        raise web.seeother("/file/recent_edit")


xurls = ("/file/edit", handler, 
        "/file/markdown", handler,
        "/file/markdown/edit", MarkdownEdit,
        "/file/update", UpdateHandler)
