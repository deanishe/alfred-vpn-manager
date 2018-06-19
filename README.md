
Alfred VPN Manager
==================

Manage your [Tunnelblick][tunnelblick] and [Viscosity][viscosity] VPN connections from [Alfred][alfred].

**Note:** Version 2 requires Alfred 3.

![Alfred-Viscosity in action][demo]

Contents
--------

<!-- MarkdownTOC autolink="true" bracket="round" depth="3" autoanchor="true" -->

- [Installation](#installation)
- [Usage](#usage)
- [Supported apps](#supported-apps)
- [What's a VPN for, anyway?](#whats-a-vpn-for-anyway)
    - [VPN providers](#vpn-providers)
- [Licence & thanks](#licence--thanks)

<!-- /MarkdownTOC -->

<a name="installation"></a>
Installation
------------

Download the `VPN-Manager-X.X.X.alfred3workflow` file from [GitHub releases][download] and double-click the file to import it into Alfred.


<a name="usage"></a>
Usage
-----

- `vpn [<query>]` — View and filter Viscosity VPN connections.
    - `↩` — Connect/disconnect selected connection.
- `vpnconf [<query>]` — View and edit workflow configuration.
    - `Workflow Update Available!` / `Workflow Is up to Date` — Workflow update availablity.
        - `↩` or `⇥` — Check for and install update.
    - `App Name (active)` — The currently selected VPN application.
    - `App Name (not installed)` — Supported, but not installed, VPN application.
        - `↩` — Go to this application's website.
    - `App Name` — Installed, but unused, application.
        - `↩` — Use this application to manage VPN connections.
    - `Online Docs` — This README.
        - `↩` — Open in your default browser.
    - `Get Help` — Workflow's [thread][forum-thread] on [AlfredForum.com][forum].
        - `↩` — Open in your default browser.
    - `Report Problem` — Workflow's GitHub issues.
        - `↩` — Open in your default browser.

If you haven't entered a query, any active VPN connections will be shown at the top of the list. Action an active connection to disconnect it.

If you are connected to multiple VPNs, an additional "Disconnect All" item will be shown first.


<a name="supported-apps"></a>
Supported apps
--------------

The workflow currently supports [Tunnelblick][tunnelblick] and [Viscosity][viscosity], which both manage [OpenVPN][openvpn] connections.

Essentially, the functionality of both applications is the same. Tunnelblick is open source and free, while Viscosity is proprietary and cheap, but has a more pleasant user interface.


<a name="whats-a-vpn-for-anyway"></a>
What's a VPN for, anyway?
-------------------------

To prevent people (geo)blocking and/or spying on you.

- So other people on the same unsecured WiFi network (or the operator) can't monitor your traffic
- To access services that are blocked on the network you're using. For example, some of the corporate networks I've used have blocked IMAP(S), so I couldn't check my email, or the iOS App Store
- To access content censored by your ISP or government
- To access services that geo-block your current location


<a name="vpn-providers"></a>
### VPN providers ###

If you don't have a VPN service yet, here are the two I personally use:

[Private Internet Access][pia] for high-bandwidth stuff, like trying to watch online videos that GEMA has blocked in Germany. The service is fast and reliable, and they [don't log your traffic][pia-nologging]. They regularly [top Torrent Freak's best VPN provider chart][torrentfreak-chart].

A self-hosted [Streisand][streisand] installation for punching through locked-down corporate firewalls that don't think I should be able to check my email. It's very simple to set up, and gives you *a lot* of options for connecting.


<a name="licence--thanks"></a>
Licence & thanks
----------------

This workflow is licensed under the [MIT Licence][mit].

It is based on the [Alfred-Workflow][aw] library (also [MIT-licensed][mit]) and the icons are from [Font Awesome][font-awesome] ([SIL OFL Licence][sil-ofl]).


[demo]: https://github.com/deanishe/alfred-viscosity/raw/master/demo.gif  "Alfred-Viscosity in action"
[tunnelblick]: https://tunnelblick.net
[viscosity]: https://www.sparklabs.com/viscosity/
[font-awesome]: http://fontawesome.io/
[alfred]: http://www.alfredapp.com/
[forum]: https://www.alfredforum.com/
[forum-thread]: https://www.alfredforum.com/topic/7333-viscosity-vpn-connection-manager/
[download]: https://github.com/deanishe/alfred-vpn-manager/releases/latest
[aw]: http://www.deanishe.net/alfred-workflow/
[mit]: http://opensource.org/licenses/MIT
[openvpn]: https://openvpn.net/
[openvpn-wiki]: https://en.wikipedia.org/wiki/OpenVPN
[pia]: https://www.privateinternetaccess.com
[pia-nologging]: https://torrentfreak.com/vpn-providers-no-logging-claims-tested-in-fbi-case-160312/
[streisand]: https://github.com/StreisandEffect/streisand
[torrentfreak-chart]: https://torrentfreak.com/vpn-services-anonymous-review-2017-170304/
[sil-ofl]: http://scripts.sil.org/cms/scripts/page.php?site_id=nrsi&id=OFL
