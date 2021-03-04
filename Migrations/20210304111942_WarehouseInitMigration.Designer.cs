﻿// <auto-generated />
using System;
using Datawarehouse_Backend.Context;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Infrastructure;
using Microsoft.EntityFrameworkCore.Migrations;
using Microsoft.EntityFrameworkCore.Storage.ValueConversion;
using Npgsql.EntityFrameworkCore.PostgreSQL.Metadata;

namespace Datawarehouse_Backend.Migrations
{
    [DbContext(typeof(WarehouseContext))]
    [Migration("20210304111942_WarehouseInitMigration")]
    partial class WarehouseInitMigration
    {
        protected override void BuildTargetModel(ModelBuilder modelBuilder)
        {
#pragma warning disable 612, 618
            modelBuilder
                .HasAnnotation("Relational:MaxIdentifierLength", 63)
                .HasAnnotation("ProductVersion", "5.0.3")
                .HasAnnotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn);

            modelBuilder.Entity("Datawarehouse_Backend.Models.AbsenceRegister", b =>
                {
                    b.Property<long>("id")
                        .ValueGeneratedOnAdd()
                        .HasColumnType("bigint")
                        .HasAnnotation("Npgsql:ValueGenerationStrategy", NpgsqlValueGenerationStrategy.IdentityByDefaultColumn);

                    b.Property<string>("abcenseType")
                        .IsRequired()
                        .HasColumnType("text");

                    b.Property<long>("absenceId")
                        .HasColumnType("bigint");

                    b.Property<string>("degreeDisability")
                        .IsRequired()
                        .HasColumnType("text");

                    b.Property<double>("duration")
                        .HasColumnType("double precision");

                    b.Property<long>("employeeId")
                        .HasColumnType("bigint");

                    b.Property<DateTime>("fromDate")
                        .HasColumnType("timestamp without time zone");

                    b.Property<bool>("soleCaretaker")
                        .HasColumnType("boolean");

                    b.Property<DateTime>("toDate")
                        .HasColumnType("timestamp without time zone");

                    b.HasKey("id");

                    b.ToTable("AbsenceRegisters");
                });
#pragma warning restore 612, 618
        }
    }
}
