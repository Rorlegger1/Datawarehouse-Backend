
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Security;
using System.Security.Claims;
using Datawarehouse_Backend.Context;
using Datawarehouse_Backend.Models;
using Datawarehouse_Backend.ViewModels;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;

/*
* This controller handles API-calls from logged in users on the website. The calls handled by this controller
* is mainly calls to fetch data from the warehouse, to be displayed in the dashboard of the website.
*/

namespace Datawarehouse_Backend.Controllers
{
    [Route("web/")]
    [ApiController]

    public class WebController : ControllerBase
    {
        private readonly IConfiguration config;
        private readonly WarehouseContext _warehouseDb;
        private readonly LoginDatabaseContext _db;

        public WebController(IConfiguration config, WarehouseContext warehouseDb, LoginDatabaseContext logindb)
        {
            this.config = config;
            this._warehouseDb = warehouseDb;
            this._db = logindb;
        }
        /*
        * Sets the filter to a pre-defined option based on what's requested, if no option is specified, all will be selected.
        * When modifying days, years or months, the timer for that day will allways be set to 00:00:00, so there is no need to
        * remove the hours aswell.
        */
        private DateTime compareDates(string time)
        {
            DateTime dateTimeNow = DateTime.Now;
            DateTime comparisonDate = dateTimeNow;
            int tempMonth = dateTimeNow.Month;
            int tempWeek = (int)dateTimeNow.DayOfWeek;
            int tempDay = dateTimeNow.Day;

            switch (time)
            {
                case "lastSevenDays":
                    comparisonDate = dateTimeNow.Date.AddDays(-7);
                    break;
                case "lastThirtyDays":
                    comparisonDate = dateTimeNow.Date.AddDays(-30);
                    break;
                case "lastTwelveMonths":
                    comparisonDate = dateTimeNow.Date.AddYears(-1);
                    break;
                case "thisWeek":
                    comparisonDate = dateTimeNow.Date.AddDays(-tempWeek + 1);
                    break;
                case "thisMonth":
                    comparisonDate = dateTimeNow.Date.AddDays(-tempDay + 1);
                    break;
                case "thisYear":
                    comparisonDate = dateTimeNow.Date.AddMonths(-tempMonth + 1).AddDays(-tempDay + 1);
                    break;
                default:
                    Console.WriteLine("No filter added, listing all..");
                    comparisonDate = dateTimeNow.Date.AddYears(-30);
                    break;
            }
            Console.WriteLine("Filter selected: " + time);
            Console.WriteLine("current date: " + dateTimeNow);
            Console.WriteLine("Filtering by: " + comparisonDate);
            return comparisonDate;
        }


        [Authorize(Roles = "User")]
        [HttpGet("accrec")]
        public List<DateStatusView> getAccountReceivables(string filter)
        {
            DateTime dateTimeNow = DateTime.Now;
            long tennantId = getTennantId();
            DateTime comparisonDate = compareDates(filter);
            var vouchers = _warehouseDb.Vouchers
            .Where(v => v.client.tennantFK == tennantId && v.date >= comparisonDate)
            .Where(d => d.Type == "outbound" || d.Type == "payment")
            .Include(c => c.invoice)
            .OrderByDescending(p => p.paymentId).ThenBy(d => d.Type)
            .ToList();
            //We now have a list of all vouchers that has date
            //after the filter given, ordered by paymentId, then by type
            // This enables us to compare voucher n to n+1
            // if n has a voucher that is paid, it will be n+1
            // and it makes sure that voucher n is the first voucher that is made on that id
            // making n the outgoing voucher, and n+1 the payment voucher
            // but only if n and n+1 has same paymentId

            // Now we find all the vouchers that has been paid too late.
            List<AccRecView> accList = new List<AccRecView>();
            for (int i = 0; i < vouchers.Count; i++)
            {
                //Even though there shouldnt be any vouchers without invoices getting through the datasubmission
                //We double check to avoid any errors, and still provide a visual feed in the frontend.
                if (vouchers[i].invoice == null)
                {
                    i++;
                }
                if (i < vouchers.Count - 1)
                {
                    //if outbound and payment has same paymentId and is paid too late
                    if (vouchers[i].paymentId == vouchers[i + 1].paymentId && vouchers[i].invoice.dueDate < vouchers[i + 1].date)
                    {
                        AccRecView view = new AccRecView();
                        Console.WriteLine("PID getting added: " + vouchers[i].paymentId);
                        view.PID = vouchers[i].paymentId;
                        view.dueDate = vouchers[i].invoice.dueDate;
                        view.payDate = vouchers[i + 1].date;
                        view.amount = vouchers[i].invoice.amountTotal;
                        view.daysDue = view.payDate.DayOfYear - view.dueDate.DayOfYear;
                        accList.Add(view);
                        i++; //Skip i+1, since we compiled i and i+1
                    }
                    //If an outbound voucher has not been paid. 
                    //Setting payDate to the date of request so that I can categorize how long overdue the payment is. 
                    else if (vouchers[i].paymentId != vouchers[i + 1].paymentId)
                    {
                        Console.WriteLine("PID: " + vouchers[i].paymentId + "has not been paid");
                        AccRecView view = new AccRecView();
                        view.PID = vouchers[i].paymentId;
                        view.dueDate = vouchers[i].invoice.dueDate;
                        view.payDate = dateTimeNow;
                        view.amount = vouchers[i].invoice.amountTotal;
                        view.daysDue = view.payDate.DayOfYear - view.dueDate.DayOfYear;
                        accList.Add(view);
                    }
                    //If the outbound voucher is paid, and paid within the duedate, skip this and next voucher.
                    else
                    {
                        i++;
                    }
                }
                //Last payment n was not connected to n-1, therefore it's an unpaid outbound invoice.
                else
                {
                    Console.WriteLine("PID: " + vouchers[i].paymentId + "has not been paid");
                    AccRecView view = new AccRecView();
                    view.PID = vouchers[i].paymentId;
                    view.dueDate = vouchers[i].invoice.dueDate;
                    view.payDate = dateTimeNow;
                    view.amount = vouchers[i].invoice.amountTotal;
                    view.daysDue = view.payDate.DayOfYear - view.dueDate.DayOfYear;
                    accList.Add(view);
                }
            }
            accList.Sort((x, y) => x.dueDate.CompareTo(y.dueDate));
            /*
            We now have a sorted list of vouchers that was paid too late, or not paid at all.

            We start at the day of the filter requested, and move with a custom timeintervall that is now set to 7days,
            all the way til we reach todays date then once more for today.
            For every step we take towards todays date, we iterate over the list of vouchers that was paid too late, or not paid at all.
            For every voucher in that list we check which duedate category it belongs to, and then add the amountdue the voucher has to the correct category
            */

            //Setting the temporary date to the first day of the filter requested.
            //And setting timeIntervall to 7 Days.
            List<DateStatusView> graphList = new List<DateStatusView>();
            DateTime tempDate = comparisonDate;
            int timeIntervall = 7;
            while (tempDate <= dateTimeNow)
            {
                DateStatusView aView = new DateStatusView();
                aView.year = tempDate.Year;
                aView.month = tempDate.Month;
                aView.day = tempDate.Day;
                aView.thirtyAmount = 0;
                aView.sixtyAmount = 0;
                aView.ninetyAmount = 0;
                aView.ninetyPlusAmount = 0;

                for (int i = 0; i < accList.Count; i++)
                {
                    Console.WriteLine("Adding data for date: " + tempDate);
                    if (accList[i].dueDate <= tempDate && tempDate <= accList[i].payDate)
                    {
                        if (accList[i].daysDue < 30)
                        {
                            aView.thirtyAmount += accList[i].amount;
                        }
                        else if (accList[i].daysDue >= 30 && accList[i].daysDue < 60)
                        {
                            aView.sixtyAmount += accList[i].amount;
                        }
                        else if (accList[i].daysDue >= 60 && accList[i].daysDue < 90)
                        {
                            aView.ninetyAmount += accList[i].amount;
                        }
                        else
                        {
                            aView.ninetyPlusAmount += accList[i].amount;
                        }
                    }
                }
                //If one week doesnt surpass today, add one week
                if (tempDate.AddDays(timeIntervall) < dateTimeNow)
                {
                    tempDate = tempDate.AddDays(timeIntervall);
                }
                // if one week surpasses todays date, set it as today
                else if (tempDate != dateTimeNow)
                {
                    tempDate = dateTimeNow;
                }
                // We have now added all dates wanted, including todays date, push it over to break the whileloop.
                else
                {
                    tempDate = dateTimeNow.AddDays(1);
                }
                graphList.Add(aView);
            }
            return graphList;
        }

        /*
        *  Takes information from all the absenceRegisters requested, and puts them into a new list of absence viewmodels which
        *  only tracks year, month and total absence for that month OR Date and total absence for that date.
        *  If it's this week/month or last 30 / 7 days it will summarize for each date instead of month.
        * So instead of getting a list of all absences, it gives a list of total absences per month/date.
        */

        [Authorize]
        [HttpGet("absence")]
        public IList<AbsenceView> getAbsenceRegister(string filter)
        {
            long tennantId = getTennantId();
            DateTime comparisonDate = compareDates(filter);
            var absence = _warehouseDb.AbsenceRegisters
            .Where(i => i.employee.tennantFK == tennantId)
            .Where(d => d.fromDate >= comparisonDate)
            .OrderBy(d => d.fromDate)
            .ToList();

            List<AbsenceView> absenceViews = new List<AbsenceView>();
            double totalAbsence = 0;
            if (filter == "thisWeek" || filter == "thisMonth" || filter == "lastThirtyDays" || filter == "lastSevenDays")
            {
                try
                {
                    for (int i = 0; i < absence.Count; i++)
                    {
                        if (i != absence.Count - 1)
                        {
                            if (absence[i].fromDate.Day == absence[i + 1].fromDate.Day)
                            { //since the list is ordered allready, we can compare current month with next, if it is, add the duration to months total
                                totalAbsence += absence[i].duration;
                                Console.WriteLine("Adding absence.." + "\nCurrent total: " + totalAbsence);
                            }
                            else
                            { // Next absence is a new month, add the current absence we're on and add the view to the new list of views.
                                totalAbsence += absence[i].duration;
                                AbsenceView view = new AbsenceView();
                                view.year = absence[i].fromDate.Year;
                                view.month = absence[i].fromDate.Month;
                                view.day = absence[i].fromDate.Day;
                                view.weekDay = absence[i].fromDate.DayOfWeek.ToString();
                                view.totalDuration = totalAbsence;
                                Console.WriteLine("Adding new absence: \nWeekDay: " + view.weekDay + "\nMonth: " + view.month + "\nYear: " + view.year + "\nTotal Duration: " + view.totalDuration);
                                absenceViews.Add(view);
                                totalAbsence = 0;
                            }
                        }
                        else if (absence[i].fromDate.Day == absence[i - 1].fromDate.Day)
                        { //last absence has the same month as the one previously added absence
                            totalAbsence += absence[i].duration;
                            AbsenceView view = new AbsenceView();
                            view.year = absence[i].fromDate.Year;
                            view.month = absence[i].fromDate.Month;
                            view.day = absence[i].fromDate.Day;
                            view.weekDay = absence[i].fromDate.DayOfWeek.ToString();
                            view.totalDuration = totalAbsence;
                            Console.WriteLine("Adding new absence: \nWeekDay: " + view.weekDay + "\nMonth: " + view.month + "\nYear: " + view.year + "\nTotal Duration: " + view.totalDuration);
                            absenceViews.Add(view);
                            totalAbsence = 0;
                        }
                        else
                        { //last absence is in a new month
                            totalAbsence += absence[i].duration;
                            AbsenceView view = new AbsenceView();
                            view.year = absence[i].fromDate.Year;
                            view.month = absence[i].fromDate.Month;
                            view.day = absence[i].fromDate.Day;
                            view.weekDay = absence[i].fromDate.DayOfWeek.ToString();
                            view.totalDuration = absence[i].duration;
                            Console.WriteLine("Adding new absence: \nWeekDay: " + view.weekDay + "\nMonth: " + view.month + "\nYear: " + view.year + "\nTotal Duration: " + view.totalDuration);
                            absenceViews.Add(view);
                            totalAbsence = 0;
                        }
                    }
                }
                catch (Exception e)
                {
                    Console.WriteLine("Error: " + e);
                }
                return absenceViews;
            }
            else  //Monthly-based filter is chosen, now we summarize for each month instead of day.
            {
                try
                {
                    for (int i = 0; i < absence.Count; i++)
                    {
                        if (i != absence.Count - 1)
                        {
                            //since the list is ordered allready, we can compare current month with next, if it is, add the duration to months total
                            if (absence[i].fromDate.Month == absence[i + 1].fromDate.Month)
                            { 
                                totalAbsence += absence[i].duration;
                                Console.WriteLine("Adding days.." + "\nCurrent total: " + totalAbsence);
                            }
                            // Next absence is a new month, add the current absence we're on and add the view to the new list of views.
                            else
                            { 
                                totalAbsence += absence[i].duration;
                                AbsenceView view = new AbsenceView();
                                view.year = absence[i].fromDate.Year;
                                view.month = absence[i].fromDate.Month;
                                view.totalDuration = totalAbsence;
                                Console.WriteLine("Adding new absence:\nMonth: " + view.month + "\nVIEW Year: " + view.year + "\nTotal Duration: " + view.totalDuration);
                                absenceViews.Add(view);
                                totalAbsence = 0;
                            }
                        }
                        //last absence has the same month as the one previously added absence
                        else if (absence[i].fromDate.Month == absence[i - 1].fromDate.Month)
                        { 
                            totalAbsence += absence[i].duration;
                            AbsenceView view = new AbsenceView();
                            view.year = absence[i].fromDate.Year;
                            view.month = absence[i].fromDate.Month;
                            view.totalDuration = totalAbsence;
                            Console.WriteLine("Adding new absence:\nMonth: " + view.month + "\nVIEW Year: " + view.year + "\nTotal Duration: " + view.totalDuration);
                            absenceViews.Add(view);
                            totalAbsence = 0;
                        }
                        //last absence is in a new month
                        else
                        { 
                            totalAbsence += absence[i].duration;
                            AbsenceView view = new AbsenceView();
                            view.year = absence[i].fromDate.Year;
                            view.month = absence[i].fromDate.Month;
                            view.totalDuration = absence[i].duration;
                            Console.WriteLine("Adding new absence:\nMonth: " + view.month + "\nVIEW Year: " + view.year + "\nTotal Duration: " + view.totalDuration);
                            absenceViews.Add(view);
                            totalAbsence = 0;
                        }
                    }
                }
                catch (Exception e)
                {
                    Console.WriteLine("Error: " + e);
                }
                return absenceViews;
            }
        }

        [Authorize]
        [HttpGet("timeregister")]
        public List<TimeRegister> getTimeRegisters(string filter)
        {
            DateTime comparisonDate = compareDates(filter);
            long tennantId = getTennantId();
            var timeRegisters = _warehouseDb.TimeRegisters
            .Where(t => t.employee.tennantFK == tennantId && t.recordDate >= comparisonDate)
            .OrderByDescending(d => d.recordDate)
            .ToList();
            return timeRegisters;
        }

        /*
        * Returns a list of all tennants orders that have an end date 
        * later than the date of the request.
        * All orders are converted to orderView that only show customer name, 
        * total amount from its invoice, jobname and end date.
        */

        [Authorize]
        [HttpGet("pendingOrders")]
        public List<OrderView> getPendingOrders()
        {
            var orders = getTennant().orders
            .Where(o => o.endDate >= DateTime.Now)
            .OrderByDescending(o => o.endDate)
            .ToList();
            List<OrderView> orderList = new List<OrderView>();
            for (int i = 0; i < orders.Count; i++)
            {
                OrderView order = new OrderView();
                order.clientName = orders[i].client.clientName;
                order.jobname = orders[i].jobName;
                order.endDate = orders[i].endDate;
                orderList.Add(order);
            }
            return orderList;
        }

        /*
        * A method to fetch all orders
        */

        [Authorize]
        [HttpGet("allOrders")]
        public List<OrderView> getAllOrders()
        {
            var orders = getTennant().orders
            .OrderByDescending(o => o.endDate)
            .ToList();
            List<OrderView> orderList = new List<OrderView>();

            for (int i = 0; i < orders.Count; i++)
            {
                OrderView order = new OrderView();
                order.clientName = orders[i].client.clientName;
                order.jobname = orders[i].jobName;
                order.endDate = orders[i].endDate;
                orderList.Add(order);
            }
            return orderList;
        }


        /*
        * A method to find all customers for a specific tennant.
        * Returns a list of customers ordered by their names.
        * The customer information returned: Name, address, zipcode, city and total AmountDue from
        * it's list of accounts receivables.
        *
        * Returns:
        * A list of customer addresses, zipcode, city and type
        *
        */

        [Authorize]
        [HttpGet("customers")]
        public List<ClientView> getCustomers()
        {
            long tennantId = getTennantId();
            var customers = _warehouseDb.Clients
            .Where(c => c.tennantFK == tennantId)
            .OrderBy(c => c.clientName)
            .ToList();

            List<ClientView> customerList = new List<ClientView>();
            for (int i = 0; i < customers.Count; i++)
            {
                ClientView cust = new ClientView();
                cust.clientName = customers[i].clientName;
                cust.address = customers[i].address;
                cust.zipcode = customers[i].zipcode;
                cust.city = customers[i].city;
                if (customers[i].customer)
                {
                    cust.type = "Customer";
                }
                else
                {
                    cust.type = "Supplier";
                }
                customerList.Add(cust);
            }
            return customerList;
        }

        /*
        * 
        */

        [Authorize]
        [HttpGet("balance")]
        public List<BnbView> getBalanceAndBudget(string filter)
        {
            DateTime comparisonDate = compareDates(filter);
            var balanceAndBudgets = getTennant().bnb
            .Where(d => d.periodDate >= comparisonDate)
            .OrderByDescending(d => d.periodDate).ToList();
            List<BnbView> bnbList = new List<BnbView>();
            for (int i = 0; i < balanceAndBudgets.Count; i++)
            {
                BnbView bnb = new BnbView();
                bnb.account = balanceAndBudgets[i].account;
                bnb.startBalance = balanceAndBudgets[i].startBalance;
                bnb.endBalance = balanceAndBudgets[i].endBalance;
                bnb.periodBalance = balanceAndBudgets[i].periodBalance;
                bnbList.Add(bnb);
            }
            return bnbList;
        }

        /*
        * Two functions that takes the first claim from the JWT Token to find which tennant/tennantId
        * their accounts is bound to.  The first function returns the object tennant based on the ID
        * The other function simply returns the tennantId that has been found.
        */

        private Tennant getTennant()
        {
            var identity = HttpContext.User.Identity as ClaimsIdentity;
            IList<Claim> claim = identity.Claims.ToList();
            long tennantId = long.Parse(claim[0].Value);
            Tennant tennant = _warehouseDb.Tennants
            .Where(t => t.id == tennantId).FirstOrDefault<Tennant>();
            return tennant;
        }
        private long getTennantId()
        {
            var identity = HttpContext.User.Identity as ClaimsIdentity;
            IList<Claim> claim = identity.Claims.ToList();
            long tennantId = long.Parse(claim[0].Value);
            return tennantId;
        }
    }
}