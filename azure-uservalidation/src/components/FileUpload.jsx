import React, { useState } from 'react';
import ResultTable from './ResultTable';
import 'bootstrap/dist/css/bootstrap.css';
import Spinner from 'react-bootstrap/Spinner';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Stack from 'react-bootstrap/Stack';
import Image from 'react-bootstrap/Image';

function FileUpload() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState({ active_users: [], not_found_users: [] });
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = () => {
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    fetch('http://localhost:5000/api/user_analysis', {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Received data from the API:", data);
        if (data.message) {
          alert(data.message);
        } else {
          setResults(data); // Set the results here
        }
      })
      .catch((error) => {
        console.error('Error:', error);
      })
      .finally(() => {
        setLoading(false); // Stop loading animation
      });
  };

  return (
    <div className="mb-2"> {/* Center content */}
    <Stack gap={5}>
    <Container>
      <Row>
        <Col xs={6} md={4}>
          <Image src="logo-281x94.png" rounded />
        </Col>
      </Row>
      <Row>
        <div className="p-2">
        <Col><Form.Group controlId="formFile" className="mb-3">
        <Form.Label>Select the Access list for inspection</Form.Label>
        <Form.Control type="file" onChange={handleFileChange} />
      </Form.Group>
      <Button variant="primary" onClick={handleUpload}>Upload and Analyze</Button></Col>
      </div>
      </Row>
      
      <Row>
        <div className="p-2" style={{ display: loading ? 'block' : 'none' }}>
        <Spinner animation="border" variant="primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        </div>
      <div className="p-2" style={{ display: loading ? 'none' : 'block' }}></div>
        <Col>
          {results.active_users.length > 0 && (
            <ResultTable title="Active Users" data={results.active_users} status="Active" />
          )}
          </Col>
        <Col>
          {results.active_users.length > 0 && (
            <ResultTable title="Not Found Users" data={results.not_found_users} status="Not Found" />
          )}
        </Col>
      </Row>
    </Container>
    </Stack>
    </div>
  );
}

export default FileUpload;
