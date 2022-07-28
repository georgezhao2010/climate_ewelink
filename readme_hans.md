# Midea Air Conditioner via eWeLink Cloud

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![Stable](https://img.shields.io/github/v/release/georgezhao2010/climate_ewelink)](https://github.com/georgezhao2010/climate_ewelink/releases/latest)

[English](https://github.com/georgezhao2010/climate_ewelink/blob/main/readme.md) | 简体中文

Home Assistant的自定义集成组件, 允许你通过易微联云控制你的美的空调.

# 提示

现在有了新的集成 [Midea AC LAN](https://github.com/georgezhao2010/midea_ac_lan) 允许你通过本地局域网而不是云来控制你的美的空调。

# 使用之前

如果你没有易微联账户，先下载易微联(eWeLink)App，注册一个账户，并在其中绑定你的美的美居账户。

# 关于易微联账户的重要内容

由于易微联的账户存在单点登录检测，因此组件也许不能与同一账户的其它方式登录（易微联App或另一个HomeAssistant）同时正常工作。
所以你可能要准备至少第二个账户，其中一个在易微联App中绑定美的账号，然后分享给另一个。然后两个账户一个用来登录HomeAssistant，另一个用来登录易微联App。

如果你的易微联账户是11位手机号码, 记得在之前加上"+86", 才是完整的易微联用户名。

# 安装

在HACS中搜索'Midea A/C via eWeLink'进行安装, 或者将位于[Latest Release](https://github.com/georgezhao2010/climate_ewelink/releases/latest)中的`custom_components/cliamte_ewelink`下所有文件手动复制到你的Home Assistant下的`<Home Assistant config folder>/custom_components/cliamte_ewelink`目录中，然后重启Home Assistant。

# 配置

安装过后，到Home Assistant的集成界面添加集成，并输入以下内容:

- 用户名 (易微联App账户)
- 密码 (易微联App账户)
- 国家 (中国或中国境外)

# 功能

## 恒温器

- 空调

## 传感器

- 户外温度传感器

## 开关:

- 节能模式
- 舒省模式
- 防直吹开关
- 水平摆风
- 垂直摆风
