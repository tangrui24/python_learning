help_str = '''\033[1;31m
    --------------------------------------  help list  ----------------------------------------------
    command:
        help: help                                          # 查看帮助信息
        start_session: start_session                        # 开启堡垒机服务
        syncdb: syncdb                                      # 初始化数据库
        create_users: create_users -f filename              # 添加堡垒机用户记录 e.g: create_users -f userprofile.yaml
        create_groups: create_groups -f filename            # 添加主机组记录 e.g: create_groups -f groups.yaml
        create_hosts: create_hosts -f filename              # 添加主机记录 e.g: create_host -f hosts.yaml
        create_remoteusers: create_remoteusers -f filename  # 添加主机用户记录 e.g: create_remoteusers -f remoteusers.yaml
      \033[0m '''

welcome = """\033[1;32m
                        ------------- Welcome [%s] login Stupidjumpserver -------------
        \033[0m """


