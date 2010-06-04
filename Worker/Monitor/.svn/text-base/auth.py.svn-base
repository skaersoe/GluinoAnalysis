from mod_python import apache

def authenhandler(req):
    pw = req.get_basic_auth_pw()
    user = req.user
    
    if user == "chi" and pw == "dup2LeX":
        return apache.OK
    else:
        return apache.HTTP_UNAUTHORIZED
        
