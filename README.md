# EnkaProfileCard

<p align="center">
    <a href="https://enka.hk4e.com/genshin/103516099.png" target="_blank">
        <img src="https://enka.hk4e.com/genshin/103516099.png" alt="example" width="500">
    </a>
<p>

基于 [Enka.Network API](https://api.enka.network/) 的游戏个人信息卡片生成工具

支持游戏：`原神`、~~`崩坏：星穹铁道`~~（开发中）

Enka.Network 使用游戏内部 API 获取数据，与米游社（HoYoLab）不同，无法获取探索度、宝箱数等数据

## 使用

访问 `https://enka.hk4e.com/genshin/{uid}.png` 将 `{uid}` 替换为游戏 UID 即可生成卡片

例如 [https://enka.hk4e.com/genshin/300000000.png](https://enka.hk4e.com/genshin/300000000.png)

玩家信息默认缓存 24 小时，生成卡片时需要获取玩家头像与角色头像，如无缓存可能需要等待数秒

## TODO

- [x] 原神支持
- [ ] 崩坏：星穹铁道支持
- [ ] 自定义背景
- [ ] 自定义字体

## Credits

[Enka.Network](https://enka.network/)  
[Enka.Network API](https://api.enka.network/)
