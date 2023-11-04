import React from 'react';
import Table from 'react-bootstrap/Table';


function ResultTable({ title, data, status }) {
  return (
    <div className="ResultTable">
      <h3>{title}:</h3>
        <Table striped bordered hover variant="dark">
          <thead>
            <tr>
              <th>First Name</th>
              <th>Last Name</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.map((user, index) => (
              <tr key={index}>
                <td>{user.first_name}</td>
                <td>{user.last_name}</td>
                <td>{status}</td>
              </tr>
            ))}
          </tbody>
        </Table>
    </div>
  );
}

export default ResultTable;
