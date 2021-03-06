<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

require("localSidebar.php");
require("graph/navbar.inc.php");

require_once("modules/pkgs/includes/xmlrpc.php");
require_once("modules/pkgs/includes/functions.php");

$p = new PageGenerator(_T("Edit package", "pkgs"));
$p->setSideMenu($sidemenu);
$p->display();

// var formating
$_GET['p_api'] = isset($_GET['p_api']) ? $_GET['p_api'] : "";

$package = array();

/*
 * File Upload
 */

if (isset($_POST["bcreate"]) || isset($_POST["bassoc"])) {
    $p_api_id = $_POST['p_api'];
    $need_assign = False;
    if ($_GET["action"]=="add") {
        $need_assign = True;
    }
    foreach (array('id', 'label', 'version', 'description') as $post) {
        $package[$post] = $_POST[$post];
    }
    foreach (array('reboot') as $post) {
        $package[$post] = ($_POST[$post] == 'on' ? 1 : 0);
    }
    foreach (array('command') as $post) {
        $package[$post] = array('name'=>$_POST[$post.'name'], 'command'=>stripslashes($_POST[$post.'cmd']));
    }
    // Send Package Infos via XMLRPC
    $ret = putPackageDetail($p_api_id, $package, $need_assign);
    if (!isXMLRPCError() and $ret and $ret != -1) {
        if ($ret[0]) {
            if ($_GET["action"]=="add") {
                #new NotifyWidgetSuccess(sprintf(_T("Package successfully added in %s", "pkgs"), $ret[2]));
                if (! isset($_POST["bassoc"])) {
                    header("Location: " . urlStrRedirect("pkgs/pkgs/index", array('location'=>base64_encode($p_api_id)))); # TODO add params to go on the good p_api
                    exit;
                }
            } else {
                new NotifyWidgetSuccess(_T("Package successfully edited", "pkgs"));
                $package = $ret[3];
            }
            if (isset($_POST["bassoc"])) {
                // If no error with sending package infos, push package previously uploaded
                $package_id = $ret[3]['id'];
                $upload_tmp_dir = sys_get_temp_dir();

                $file_list = get_directory_list($upload_tmp_dir . '/' . $random_dir);

                $files = array();
                foreach ($file_list as $filename) {
                    $file = $upload_tmp_dir . '/' . $random_dir . '/' . $filename;
                    // Read and put content of $file to $filebinary
                    $filebinary = fread(fopen($file, "r"), filesize($file));
                    $files[] = array(
                        "filename" => $filename,
                        "filebinary" => base64_encode($filebinary),
                    );
                }

                $push_package_result = pushPackage($p_api_id, $random_dir, $files);
                // Delete package from PHP /tmp dir
                delete_directory($upload_tmp_dir . '/' . $random_dir);

                if (!isXMLRPCError() and $push_package_result) {
                    header("Location: " . urlStrRedirect("pkgs/pkgs/associate_files", array('p_api'=>base64_encode($p_api_id), 'random_dir'=>base64_encode($random_dir), 'pid'=>base64_encode($ret[3]['id']), 'plabel'=>base64_encode($ret[3]['label']), 'pversion'=>base64_encode($ret[3]['version']))));
                    exit;
                }
            }
        } else {
            new NotifyWidgetFailure($ret[1]);
        }
    } else {
        new NotifyWidgetFailure(_T("Package failed to save", "pkgs"));
    }
}

$p_api_id = base64_decode($_GET['p_api']);

if (count($package) == 0 ) {
    $title = _T("Edit a package", "pkgs");
    $activeItem = "index";
    # get existing package
    $pid = base64_decode($_GET['pid']);
    $package = getPackageDetail($p_api_id, $pid);
    if ($package['do_reboot']) {
        $package['reboot'] = $package['do_reboot'];
    }
    $formElt = new HiddenTpl("id");

    $selectpapi = new HiddenTpl('p_api');
    $p_api_number = count(getUserPackageApi());
} else {
    $formElt = new HiddenTpl("id");
    $selectpapi = new HiddenTpl('p_api');
}

/*
 * Page form
 */

// display an edit package form (description, version, ...)
$f = new ValidatingForm();
$f->push(new Table());

$p_api_id = ($_GET['p_api']) ? base64_decode($_GET['p_api']) : base64_decode($_POST['p_api']);
$selectpapi = new HiddenTpl('p_api');

if ($p_api_number > 1) {
    $f->add(
        new TrFormElement(_T("Package API", "pkgs"), $selectpapi),
        array("value" => $p_api_id, "hide" => $hide)
    );
}
else {
    $f->add(
        $selectpapi,
        array("value" => $p_api_id, "hide" => True)
    );
}

$f->add(new HiddenTpl("id"), array("value" => $package['id'], "hide" => True));

if ($_GET["action"]=="add") {
    $f->add(new HiddenTpl("mode"), array("value" => "creation", "hide" => True));
}

$fields = array(
    array("label", _T("Package label", "pkgs"), array("required" => True)),
    array("version", _T("Package version", "pkgs"), array("required" => True)),
    array('description', _T("Description", "pkgs"), array()),
);

$cmds = array(
    array('command', _T('Command\'s name : ', 'pkgs'), _T('Command : ', 'pkgs')),/*
    array('installInit', _T('installInit', 'pkgs'), _T('Install Init', 'pkgs')),
    array('preCommand', _T('preCommand', 'pkgs'), _T('Pre Command', 'pkgs')),
    array('postCommandFailure', _T('postCommandFailure', 'pkgs'), _T('postCommandFailure', 'pkgs')),
    array('postCommandSuccess', _T('postCommandSuccess', 'pkgs'), _T('postCommandSuccess', 'pkgs')) //*/
);

$options = array(
    array('reboot', _T('Need a reboot ?', 'pkgs'))
);

foreach ($fields as $p) {
    $f->add(
        new TrFormElement($p[1], new InputTpl($p[0])),
        array_merge(array("value" => $package[$p[0]]), $p[2])
    );
}

foreach ($options as $p) {
    $op = ($package[$p[0]] == 1 || $package[$p[0]] == '1' || $package[$p[0]] === 'enable');
    $f->add(
        new TrFormElement($p[1], new CheckboxTpl($p[0])),
        array("value" => ($op ? 'checked' : ''))
    );
}

foreach ($cmds as $p) {
    $f->add(
        new HiddenTpl($p[0].'name'),
        array("value" => $package[$p[0]]['name'], "hide" => True)
    );
    $f->add(
        new TrFormElement($p[2], new TextareaTpl($p[0].'cmd')),
        array("value" => htmlspecialchars($package[$p[0]]['command']))
    );
}

$f->pop();

$f->addValidateButton("bcreate");

$f->display();

?>
