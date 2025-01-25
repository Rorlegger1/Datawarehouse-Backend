using System;
using System.ComponentModel.DataAnnotations;

namespace Datawarehouse_Backend.Models
{
    public class KPIMetrics
    {
        [Key]
        public int Id { get; set; }
        public DateTime Date { get; set; }

        // Financial KPIs
        public decimal Revenue { get; set; }
        public decimal OperatingMargin { get; set; }
        public decimal CashFlow { get; set; }
        public decimal OrderIntake { get; set; }

        // Operational KPIs
        public decimal ProjectProfitability { get; set; }
        public decimal CapacityUtilization { get; set; }
        public decimal DeliveryPrecision { get; set; }
        public decimal Productivity { get; set; }

        // Customer KPIs
        public decimal CustomerSatisfactionScore { get; set; }
        public int NewCustomersCount { get; set; }
        public decimal CustomerRetentionRate { get; set; }
        public int ComplaintsCount { get; set; }

        // Employee KPIs
        public decimal EmployeeSatisfactionScore { get; set; }
        public decimal SickLeaveRate { get; set; }
        public decimal TurnoverRate { get; set; }
        public int HSEIncidents { get; set; }

        // References to related entities
        public int? FinancialYearId { get; set; }
        public virtual FinancialYear FinancialYear { get; set; }

        // Metadata
        public DateTime LastUpdated { get; set; }
        public string UpdatedBy { get; set; }
        public string DataSource { get; set; }
    }
} 