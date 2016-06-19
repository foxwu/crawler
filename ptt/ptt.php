<?php
$filename = $argv[1];
$board = getBoardName($filename);
$content = file_get_contents(/* file path to load output file*/);
$object = json_decode($content, true);
$data = $object["data"];

foreach($data as $post) {
    $like = $post['count'];
    $link = "https://www.ptt.cc" . $post['link'];
    $date = $post['date'];
    $title = trim($post['title']);
    $author = $post['author'];
    $msg = array(
        "channel"       => "#pttpopular",
        "text"          => "--\n_{$board}_\n`$like` <$link|$title>\n$date by $author",
    );

    postSlack($msg);
}

function postSlack($msg) {
    $url = ""; // slack incoming webhook url
    $payload = "payload=".json_encode($msg);

    $ch = curl_init($url);

    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "POST");
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false);

    $result = curl_exec($ch);

    curl_close($ch);
}

function getBoardName($filename) {
    switch ($filename) {
        case "gossip_output.json":
            return "Gossiping";
        case "joke_output.json":
            return "Joke";
        default:
            return "Unknown";
    }
}
?>
