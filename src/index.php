<h1>Hello Skitude!</h1>
<h4>Attempting MySQL connection from php...</h4>
<?php
$host = 'mysql';
$user = 'root';
$pass = 'rootpassword';
$db = 'usuaris';
$conn = new mysqli($host, $user, $pass, $db);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
} 
echo "Connected Successfully <br>";

$sql = "SELECT * FROM usuaris;";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // output data of each row
    while($row = $result->fetch_assoc()) {
        echo $row["id"]. " - Name: " . $row["nom"]. " " . $row["cognom"]. "<br>";
    }
} else {
    echo "0 results";
}
$conn->close();
?>
