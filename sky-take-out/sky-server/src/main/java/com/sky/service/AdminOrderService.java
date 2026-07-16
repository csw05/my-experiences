package com.sky.service;

import com.sky.dto.*;
import com.sky.result.PageResult;
import com.sky.vo.OrderStatisticsVO;
import com.sky.vo.OrderVO;

public interface AdminOrderService {
    PageResult conditionSearch(OrdersPageQueryDTO ordersPageQueryDTO);
    OrderVO details(Long id);
    void confirm(Long id);
    void rejection(OrdersRejectionDTO ordersRejectionDTO);
    void delivery(Long id);
    void complete(Long id);
    void cancel(OrdersCancelDTO ordersCancelDTO);
    OrderStatisticsVO statistics();
}