import { Component, OnInit } from '@angular/core';
import { Chart } from 'chart.js/auto';
import { CertificationRequestService } from '../../../services/certification-request/certification-request.service';
import { AlertService } from '../../../services/alert/alert.service';
import { UserService } from '../../../services/user/user.service';
import { EncodingService } from '../../../services/encoding/encoding.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [],
  templateUrl: './admin-dashboard.component.html',
  styleUrl: './admin-dashboard.component.css'
})
export class AdminDashboardComponent implements OnInit {
  protected certificationChart:any;
  protected encodingsChart:any;
  protected userChart:any;
  constructor(private alert:AlertService, private certificationRequestService:CertificationRequestService, private userService:UserService, private encodingService:EncodingService) { }

  ngOnInit(): void {
    this.initCertificationChart();
    this.initEncodingsChart();
    this.initUserChart();
  }
  initUserChart() {
    this.alert.showSpinner();
    const data = {
      labels: ['Total', 'Disabled', 'Active', 'Oauth2 logins', 'Username and password logins'],
      datasets: [{
        data: [0, 0, 0, 0, 0],
        backgroundColor: [
          'rgba(54, 162, 235, 0.2)',   // Blue with 0.2 opacity for 'Total'
          'rgba(255, 99, 132, 0.2)',   // Red with 0.2 opacity for 'Disabled'
          'rgba(75, 192, 192, 0.2)',   // Green with 0.2 opacity for 'Active'
          'rgba(201, 203, 207, 0.2)',  // Grey with 0.2 opacity for 'Oauth2 logins'
          'rgba(255, 159, 64, 0.2)'    // Orange with 0.2 opacity for 'Username and password logins'
        ],
        borderColor: [
          'rgba(54, 162, 235, 1)',     // Blue for 'Total'
          'rgba(255, 99, 132, 1)',     // Red for 'Disabled'
          'rgba(75, 192, 192, 1)',     // Green for 'Active'
          'rgba(201, 203, 207, 1)',    // Grey for 'Oauth2 logins'
          'rgba(255, 159, 64, 1)'      // Orange for 'Username and password logins'
        ],
        borderWidth: 1
      }]
    };
    this.userChart = new Chart('userChart', {
      type: 'bar',
      data: data,
      options: {
        plugins: {
          legend: {
            display: false
          }
        },
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    });
    this.userService.getUserCount().subscribe((data) => {
    // Update the chart data without recreating the chart
    this.userChart.data.datasets[0].data = [data.total, data.disabled, data.active, data.oauth2, data.username_password];
    this.userChart.update();  // Update the chart to reflect changes
    this.alert.hideSpinner();
    }, (error) => {
      this.alert.hideSpinner();});
  }



  initEncodingsChart() {
     const data ={
      labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
      datasets: [
        {
          label: 'Encodings uploaded',
          data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          fill: true,
          backgroundColor: 'rgba(123, 104, 238, 0.2)',  // Light purple with 0.2 opacity
          borderColor: '#7B68EE',  // Medium purple
          pointBackgroundColor: '#7B68EE',  // Medium purple
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#7B68EE'  // Medium purple
        }]
    };
    this.encodingsChart= new Chart('encodingsChart', {
      type: 'radar',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        elements: {
          line: {
            borderWidth: 3
          }
        }
      },
    });
    this.encodingService.getEncodingsCount().subscribe((data) => {
      // Update the chart data without recreating the chart
      for (let i = 0; i < data.count.length; i++) {
        this.encodingsChart.data.datasets[0].data[data.count[i][0] - 1] = data.count[i][1];
      }
      
      this.encodingsChart.update();  // Update the chart to reflect changes
      this.alert.hideSpinner();
    });
  }





  initCertificationChart() {
    this.alert.showSpinner();
    const chartData = {
        labels: ['Users verified', 'Users verification rejected', "Users verification pending"],
        datasets: [
            {
                data: [0, 0, 0],
                backgroundColor: ['#3F51B5', '#f54242', '#FFD700'],  // $primary, soft red, and soft yellow
                hoverBackgroundColor: ['#3F51B5', '#FF6961', '#FFD700']  // $primary, soft red, and soft yellow
            }]
    };
    this.certificationChart = new Chart('certificationChart', {
        type: 'doughnut',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
        },
    });

    this.certificationRequestService.getCertificationRequestsCount().subscribe((data) => {
        // Update the chart data without recreating the chart
        this.certificationChart.data.datasets[0].data = [data.approved, data.rejected, data.pending];
        this.certificationChart.update();  // Update the chart to reflect changes
        this.alert.hideSpinner();
    }, (error) => {
        this.alert.hideSpinner();
    });
}


}
