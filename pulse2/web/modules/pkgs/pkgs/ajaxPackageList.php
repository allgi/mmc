<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/msc/includes/package_api.php");
require_once("modules/msc/includes/utilities.php");

global $conf;
$maxperpage = $conf["global"]["maxperpage"];

$filter = array('filter'=> $_GET["filter"], 'location'=> $_GET['location']);
$filter1 = $_GET["filter"]. '##'.$_GET['location'];

if ($_GET['location']) {
    $filter['packageapi'] = getPApiDetail(base64_decode($_GET['location']));
}
if (isset($_GET["start"])) {
    $start = $_GET["start"];
} else {
    $start = 0;
}

$packages = advGetAllPackages($filter, $start, $start + $maxperpage);
$count = $packages[0];
$packages = $packages[1];

$desc = $params = $names = $versions = $size = array();
$err = array();
foreach ($packages as $p) {
    $p = $p[0];
    if (isset($p['ERR']) && $p['ERR'] == 'PULSE2ERROR_GETALLPACKAGE') {
        $err[] = sprintf(_T("MMC failed to contact package server %s.", "pkgs"), $p['mirror']);
    } else {
        $names[] = $p['label'];
        $versions[] = $p['version'];
        $desc[] = $p['description'];
        $size[] = prettyOctetDisplay($p['size']);
        $params[] = array('p_api'=>$_GET['location'], 'pid'=>base64_encode($p['id']));
    }
}
if ($err) {
    new NotifyWidgetFailure(implode('<br/>', array_merge($err, array(_T("Please contact your administrator.", "pkgs")))));
}

$n = new OptimizedListInfos($names, _T("Package name", "pkgs"));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();
$n->addExtraInfo($desc, _T("Description", "pkgs"));
$n->addExtraInfo($versions, _T("Version", "pkgs"));
$n->addExtraInfo($size, _T("Package size", "pkgs"));
$n->setItemCount($count);
$n->setNavBar(new AjaxNavBar($count, $filter1));
$n->setParamInfo($params);
$n->start = 0;
$n->end = $count;

$n->addActionItem(new ActionItem(_T("Edit a package", "pkgs"),"edit","edit","pkgs", "pkgs", "pkgs"));
$n->addActionItem(new ActionPopupItem(_T("Delete a package", "pkgs"),"delete","delete","pkgs", "pkgs", "pkgs"));

print "<br/><br/>"; // to go below the location bar : FIXME, really ugly as line height dependent

$n->display();

?>
