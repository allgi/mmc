<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php

require_once("../config.inc.php");

$name = $_POST['minputname'];

require_once("../i18n.inc.php");
require_once("../acl.inc.php");
require_once("../session.inc.php");

require_once ("../PageGenerator.php");
require_once ("../FormGenerator.php");



$arr = $_POST[$name];

if (isset($_POST['del'])) {
    if (count($arr)>1) {
       unset($arr[$_POST['del']]);
    }
} else {
    $arr[]= '';
}

$arr = array_values($arr);


$test = new FormElement(_T($name,"mail"),new MultipleInputTpl($name,urldecode($_POST['desc'])));
$test->setCssError($name);
$test->display($arr);

/*print '<pre>';
//print_r($_GET);
print_r($_POST);
print '</pre>';*/