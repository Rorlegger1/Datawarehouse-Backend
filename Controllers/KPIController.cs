using System;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Linq;
using Datawarehouse_Backend.Models;
using System.Collections.Generic;

namespace Datawarehouse_Backend.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class KPIController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public KPIController(ApplicationDbContext context)
        {
            _context = context;
        }

        // GET: api/KPI/financial/{year}
        [HttpGet("financial/{year}")]
        public async Task<ActionResult<IEnumerable<KPIMetrics>>> GetFinancialKPIs(int year)
        {
            var kpis = await _context.KPIMetrics
                .Where(k => k.Date.Year == year)
                .OrderBy(k => k.Date)
                .ToListAsync();

            return Ok(kpis);
        }

        // POST: api/KPI/collect
        [HttpPost("collect")]
        public async Task<ActionResult<KPIMetrics>> CollectKPIData()
        {
            var kpiMetrics = new KPIMetrics
            {
                Date = DateTime.UtcNow,
                LastUpdated = DateTime.UtcNow,
                DataSource = "Cordel 2.1"
            };

            // Collect Financial KPIs
            var financialData = await _context.FinancialYear
                .OrderByDescending(f => f.Year)
                .FirstOrDefaultAsync();

            if (financialData != null)
            {
                kpiMetrics.FinancialYearId = financialData.Id;
                // Add logic to calculate financial metrics
            }

            // Collect Employee KPIs
            var employeeData = await _context.AbsenceRegister
                .Where(a => a.Date.Month == DateTime.UtcNow.Month)
                .ToListAsync();

            if (employeeData.Any())
            {
                kpiMetrics.SickLeaveRate = CalculateSickLeaveRate(employeeData);
            }

            // Add to database
            _context.KPIMetrics.Add(kpiMetrics);
            await _context.SaveChangesAsync();

            return CreatedAtAction(nameof(GetFinancialKPIs), new { year = kpiMetrics.Date.Year }, kpiMetrics);
        }

        private decimal CalculateSickLeaveRate(List<AbsenceRegister> absences)
        {
            // Add calculation logic
            return absences.Count > 0 ? (decimal)absences.Count / 30 : 0;
        }
    }
} 