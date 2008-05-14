<?php

require_once("modules/inventory/includes/xmlrpc.php");

$table = $_GET['table'];
$get_uuid = $_GET['uuid'];
$gid = $_GET['gid'];

ob_end_clean();

$filename = implode('.', explode('|', $table));
header("Content-type: text/txt");
header('Content-Disposition: attachment; filename="'.$filename.'.csv"');

$tables = explode('|', $table);

$datum = array();
if (count($tables) > 1) {
    foreach ($tables as $table) {
        $machines = getLastMachineInventoryPart($table, array('gid'=>$gid, 'uuid'=>$get_uuid));
        foreach ($machines as $machine) {
            $name = $machine[0];
            $uuid = $machine[2];
            $content = $machine[1];
            if ($datum[$uuid] == null) {
                $datum[$uuid] = array($name, array(), $uuid);
            }
            foreach ($content as $k=>$v) {
                $datum[$uuid][1][$k] = $v; // = $datum[$uuid][1] + $content;
            }
        }
    }
    $datum = array_values($datum);
} else {
    $datum = getLastMachineInventoryPart($table, array('gid'=>$gid, 'uuid'=>$get_uuid));
}

$firstline = true;
foreach ($datum as $machine) {
    $name = $machine[0];
    $uuid = $machine[2];
    $content = $machine[1];
    if ($firstline) {
        print "\"Machine\",\"".implode('","', array_keys($content[0]))."\"\n";
        $firstline = false;
    }
    foreach ($content as $line) {
        print "\"$name\",\"".implode('","', array_values($line))."\"\n";
    }
}

exit;

?>


