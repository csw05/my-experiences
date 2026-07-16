package com.sky.service.impl;

import com.sky.entity.Orders;
import com.sky.mapper.OrderMapper;
import com.sky.mapper.UserMapper;
import com.sky.service.ReportService;
import com.sky.service.WorkspaceService;
import com.sky.vo.*;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang.StringUtils;
import org.apache.poi.xssf.usermodel.XSSFRow;
import org.apache.poi.xssf.usermodel.XSSFSheet;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import javax.servlet.ServletOutputStream;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@Slf4j
public class ReportServiceImpl implements ReportService {

    @Autowired
    private OrderMapper orderMapper;
    @Autowired
    private UserMapper userMapper;
    @Autowired
    private WorkspaceService workspaceService;

    public TurnoverReportVO getTurnover(LocalDate begin, LocalDate end) {
        List<LocalDate> dateList = new ArrayList<>();
        dateList.add(begin);
        LocalDate cur = begin;
        while (!cur.equals(end)) {
            cur = cur.plusDays(1);
            dateList.add(cur);
        }
        List<Double> turnoverList = new ArrayList<>();
        for (LocalDate date : dateList) {
            LocalDateTime beginTime = LocalDateTime.of(date, LocalTime.MIN);
            LocalDateTime endTime = LocalDateTime.of(date, LocalTime.MAX);
            Map<String, Object> map = new HashMap<>();
            map.put("status", Orders.COMPLETED);
            map.put("begin", beginTime);
            map.put("end", endTime);
            Double turnover = orderMapper.sumByMap(map);
            turnover = turnover == null ? 0.0 : turnover;
            turnoverList.add(turnover);
        }
        return TurnoverReportVO.builder()
                .dateList(StringUtils.join(dateList, ","))
                .turnoverList(StringUtils.join(turnoverList, ","))
                .build();
    }

    public UserReportVO getUserStatistics(LocalDate begin, LocalDate end) {
        List<LocalDate> dateList = new ArrayList<>();
        dateList.add(begin);
        LocalDate cur = begin;
        while (!cur.equals(end)) {
            cur = cur.plusDays(1);
            dateList.add(cur);
        }
        List<Integer> newUserList = new ArrayList<>();
        List<Integer> totalUserList = new ArrayList<>();
        for (LocalDate date : dateList) {
            LocalDateTime beginTime = LocalDateTime.of(date, LocalTime.MIN);
            LocalDateTime endTime = LocalDateTime.of(date, LocalTime.MAX);
            Map<String, Object> map = new HashMap<>();
            map.put("end", endTime);
            Integer total = userMapper.countByMap(map);
            map.put("begin", beginTime);
            Integer news = userMapper.countByMap(map);
            newUserList.add(news == null ? 0 : news);
            totalUserList.add(total == null ? 0 : total);
        }
        return UserReportVO.builder()
                .dateList(StringUtils.join(dateList, ","))
                .newUserList(StringUtils.join(newUserList, ","))
                .totalUserList(StringUtils.join(totalUserList, ","))
                .build();
    }

    public OrderReportVO getOrderStatistics(LocalDate begin, LocalDate end) {
        List<LocalDate> dateList = new ArrayList<>();
        dateList.add(begin);
        LocalDate cur = begin;
        while (!cur.equals(end)) {
            cur = cur.plusDays(1);
            dateList.add(cur);
        }
        List<Integer> orderCountList = new ArrayList<>();
        List<Integer> validOrderCountList = new ArrayList<>();
        Integer totalOrderCount = 0;
        Integer totalValidCount = 0;
        for (LocalDate date : dateList) {
            LocalDateTime beginTime = LocalDateTime.of(date, LocalTime.MIN);
            LocalDateTime endTime = LocalDateTime.of(date, LocalTime.MAX);
            Map<String, Object> map = new HashMap<>();
            map.put("begin", beginTime);
            map.put("end", endTime);
            // total orders
            map.put("status", null);
            Integer count = orderMapper.countByMap(map);
            count = count == null ? 0 : count;
            orderCountList.add(count);
            totalOrderCount += count;
            // valid orders (completed)
            map.put("status", Orders.COMPLETED);
            Integer validCount = orderMapper.countByMap(map);
            validCount = validCount == null ? 0 : validCount;
            validOrderCountList.add(validCount);
            totalValidCount += validCount;
        }
        return OrderReportVO.builder()
                .dateList(StringUtils.join(dateList, ","))
                .orderCountList(StringUtils.join(orderCountList, ","))
                .validOrderCountList(StringUtils.join(validOrderCountList, ","))
                .totalOrderCount(totalOrderCount)
                .validOrderCount(totalValidCount)
                .orderCompletionRate(totalOrderCount == 0 ? 0.0 : totalValidCount * 1.0 / totalOrderCount)
                .build();
    }

    public SalesTop10ReportVO getSalesTop10(LocalDate begin, LocalDate end) {
        LocalDateTime beginTime = LocalDateTime.of(begin, LocalTime.MIN);
        LocalDateTime endTime = LocalDateTime.of(end, LocalTime.MAX);
        List<com.sky.dto.GoodsSalesDTO> list = orderMapper.getSalesTop(beginTime, endTime);
        List<String> nameList = list.stream().map(com.sky.dto.GoodsSalesDTO::getName).collect(Collectors.toList());
        List<Integer> numberList = list.stream().map(com.sky.dto.GoodsSalesDTO::getNumber).collect(Collectors.toList());
        return SalesTop10ReportVO.builder()
                .nameList(StringUtils.join(nameList, ","))
                .numberList(StringUtils.join(numberList, ","))
                .build();
    }

    public void exportBusinessData(HttpServletResponse response) {
        LocalDate begin = LocalDate.now().minusDays(30);
        LocalDate end = LocalDate.now().minusDays(1);
        BusinessDataVO businessData = workspaceService.getBusinessData(
                LocalDateTime.of(begin, LocalTime.MIN), LocalDateTime.of(end, LocalTime.MAX));

        XSSFWorkbook excel = new XSSFWorkbook();
        XSSFSheet sheet = excel.createSheet("Sheet1");

        // 概览标题行
        sheet.createRow(0).createCell(0).setCellValue("时间：" + begin + " 至 " + end);
        XSSFRow row = sheet.createRow(2);
        row.createCell(1).setCellValue("营业额");
        row.createCell(2).setCellValue(businessData.getTurnover());
        row.createCell(4).setCellValue("订单完成率");
        row.createCell(5).setCellValue(businessData.getOrderCompletionRate());
        row.createCell(6).setCellValue("新增用户");
        row.createCell(7).setCellValue(businessData.getNewUsers());
        row = sheet.createRow(3);
        row.createCell(1).setCellValue("有效订单");
        row.createCell(2).setCellValue(businessData.getValidOrderCount());
        row.createCell(4).setCellValue("平均客单价");
        row.createCell(5).setCellValue(businessData.getUnitPrice());

        // 明细表头
        row = sheet.createRow(5);
        row.createCell(0).setCellValue("日期"); row.createCell(1).setCellValue("营业额");
        row.createCell(2).setCellValue("有效订单"); row.createCell(3).setCellValue("订单完成率");
        row.createCell(4).setCellValue("客单价"); row.createCell(5).setCellValue("新增用户");

        for (int i = 0; i < 30; i++) {
            LocalDate date = begin.plusDays(i);
            BusinessDataVO dayData = workspaceService.getBusinessData(
                    LocalDateTime.of(date, LocalTime.MIN), LocalDateTime.of(date, LocalTime.MAX));
            row = sheet.createRow(6 + i);
            row.createCell(0).setCellValue(date.toString());
            row.createCell(1).setCellValue(dayData.getTurnover());
            row.createCell(2).setCellValue(dayData.getValidOrderCount());
            row.createCell(3).setCellValue(dayData.getOrderCompletionRate());
            row.createCell(4).setCellValue(dayData.getUnitPrice());
            row.createCell(5).setCellValue(dayData.getNewUsers());
        }

        try {
            response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
            response.setHeader("Content-Disposition", "attachment;filename=运营数据报表.xlsx");
            ServletOutputStream out = response.getOutputStream();
            excel.write(out);
            out.flush();
            out.close();
            excel.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}